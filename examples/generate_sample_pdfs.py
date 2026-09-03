"""生成 examples/ 下的演示 PDF(纯标准库,无第三方依赖)。

为什么需要这个脚本:
- 示例 PDF 不能使用真实候选人的简历;
- 仓库里需要一个"文本稳定、可被 pypdf 提取"的 PDF 用于 parse/extract/score 演示与测试,
  手工能控制其内容,因此用代码生成而不是找任意现成 PDF。

生成内容:
- examples/resume.pdf:一份两页的虚拟简历(ASCII 文本),用于验证"多页拼接";
- examples/blank.pdf:一页空白 PDF,用于验证"PDF 能打开但无文本"的错误分支。

为什么用 Helvetica:它是 PDF 内置的 14 种标准字体之一,无需嵌入字体文件;
内容限定为 ASCII 文本,保证任何 PDF 解析器都能按 WinAnsi 编码还原原文。
如需真正的中文简历演示,可在 Phase 后续用 Word/WPS 等导出 PDF 后替换 examples/resume.pdf。

运行方式:
    .venv/bin/python examples/generate_sample_pdfs.py
"""

from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent


def _content_stream(lines: list[str]) -> bytes:
    """把若干 ASCII 文本行拼成一个 PDF 内容流(content stream)。"""
    assert all(line.isascii() for line in lines), "示例 PDF 内容仅支持 ASCII"

    ops: list[str] = ["BT", "/F1 12 Tf", "60 740 Td"]
    for line in lines:
        # 文本串里若含括号/反斜杠需要转义,否则会破坏 PDF 字符串语法。
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        ops.append(f"({escaped}) Tj")
        ops.append("0 -18 Td")  # 每行相对下移 18pt
    ops.append("ET")
    return "\n".join(ops).encode("ascii")


def _build_pdf(pages_lines: list[list[str]]) -> bytes:
    """按对象编号顺序构造一个极简 PDF,并计算正确的 xref 偏移。"""
    payloads: list[bytes | None] = [None]  # 占位 index 0,对象编号从 1 开始

    # obj 1:Catalog(文档目录)
    payloads.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    # obj 2:Pages(占位,等确定子页对象编号后再填充)
    payloads.append(None)
    # obj 3:字体(Helvetica 标准字体)
    payloads.append(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding >>"
    )

    kids: list[int] = []
    for lines in pages_lines:
        page_num = len(payloads)      # 当前页对象编号
        content_num = page_num + 1    # 紧跟其后的内容流对象编号
        kids.append(page_num)

        content = _content_stream(lines)
        content_obj = (
            f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
            + content
            + b"\nendstream"
        )
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_num} 0 R "
            f"/Resources << /Font << /F1 3 0 R >> >> >>"
        ).encode("ascii")

        payloads.append(page_obj)
        payloads.append(content_obj)

    kids_refs = b" ".join(f"{k} 0 R".encode() for k in kids)
    payloads[2] = b"<< /Type /Pages /Kids [" + kids_refs + b"] /Count %d >>" % len(kids)

    # 组装 PDF 正文,并记录每个对象的起始字节偏移(用于 xref)。
    data = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for num, payload in enumerate(payloads):
        if payload is None:
            continue
        offsets[num] = len(data)
        data += f"{num} 0 obj\n".encode("ascii")
        data += payload
        data += b"\nendobj\n"

    # 写 xref 交叉引用表 + trailer。偏移必须精确指向每个 "N 0 obj" 的 N。
    xref_pos = len(data)
    object_count = len(payloads) - 1
    data += b"xref\n"
    data += f"0 {object_count + 1}\n".encode("ascii")
    data += b"0000000000 65535 f \n"  # 第 0 号对象永远是 free 项
    for num in range(1, object_count + 1):
        data += f"{offsets[num]:010d} 00000 n \n".encode("ascii")

    data += (
        f"trailer\n<< /Size {object_count + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF"
    ).encode("ascii")
    return bytes(data)


RESUME_PAGE_1 = [
    "Zhang San",
    "13800138000",
    "zhangsan@example.com",
    "",
    "Education",
    "Peking University",
    "Computer Science",
    "Bachelor",
    "2016 - 2020",
]

RESUME_PAGE_2 = [
    "Skills",
    "Python, Go, FastAPI, PostgreSQL, React",
    "",
    "Experience",
    "Backend Engineer at Example Corp",
    "Built a RAG service with Python and FastAPI",
    "Designed PostgreSQL schemas for AI features",
]


def main() -> None:
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    (EXAMPLES_DIR / "resume.pdf").write_bytes(_build_pdf([RESUME_PAGE_1, RESUME_PAGE_2]))
    (EXAMPLES_DIR / "blank.pdf").write_bytes(_build_pdf([[]]))
    print("Generated:")
    print("  examples/resume.pdf  (2 pages)")
    print("  examples/blank.pdf   (1 blank page)")


if __name__ == "__main__":
    main()
