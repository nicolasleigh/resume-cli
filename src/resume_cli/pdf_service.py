"""PDF 服务:输入文件校验与文本提取。

- validate_pdf_file:解析前的基础校验(Phase 1);
- extract_text:把 PDF 全文提取为字符串(Phase 2)。
"""

from pathlib import Path

from pypdf import PdfReader

from resume_cli.errors import (
    EmptyPDFError,
    NotPDFError,
    PDFNotFoundError,
    PDFReadError,
    PathIsNotFileError,
)


def validate_pdf_file(pdf_path: Path) -> Path:
    """校验 PDF 输入文件,合法则原样返回路径,否则抛出对应 ResumeCliError。

    共四层检查,按顺序执行:
    1. 文件是否存在;
    2. 是否是普通文件(排除目录);
    3. 扩展名是否为 .pdf;
    4. 能否被 PDF 解析器真正打开。

    第 4 层是关键:仅凭扩展名不能判断一个文件真的是 PDF。
    例如一个内容是纯文本、只是被改名为 .pdf 的文件,会在这里被拒绝。
    """
    if not pdf_path.exists():
        raise PDFNotFoundError(f"PDF file does not exist:\n{pdf_path}")

    if not pdf_path.is_file():
        raise PathIsNotFileError("input path is not a file")

    if pdf_path.suffix.lower() != ".pdf":
        raise NotPDFError("input file must be a PDF")

    try:
        PdfReader(str(pdf_path))
    except Exception as exc:
        # pypdf 对损坏、加密或伪造的 PDF 会抛出多种不同的异常,
        # 这里统一转成对用户友好的 PDFReadError,避免 traceback 泄漏。
        raise PDFReadError(f"PDF file cannot be read:\n{pdf_path}") from exc

    return pdf_path


def extract_text(pdf_path: Path) -> str:
    """读取 PDF 并返回所有页面的拼接文本。

    为什么遍历所有页面:简历 PDF 往往不止一页,只有遍历每一页、
    把全部页面文本拼成一份完整文本,后续 AI 解析才能看到完整信息。
    页面之间插入换行,避免两页边界处的文字粘连。

    若 PDF 能打开但所有页面都提取不到文本(典型是纯扫描图片 PDF),
    则抛 EmptyPDFError;本项目 MVP 不支持 OCR,README 中会说明这一点。
    """
    validate_pdf_file(pdf_path)

    reader = PdfReader(str(pdf_path))
    page_texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            # 单页内部先做 strip,拼接时用换行分隔,保证整份文本干净。
            page_texts.append(text.strip())

    full_text = "\n".join(page_texts).strip()
    if not full_text:
        raise EmptyPDFError("PDF contains no extractable text")

    return full_text
