"""PDF 服务:输入文件校验与文本提取。

Phase 1 只实现"真正解析 PDF 之前"的输入文件基础校验;
文本提取(extract_text)将在后续 Phase 加入本模块。
"""

from pathlib import Path

from pypdf import PdfReader

from resume_cli.errors import (
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
