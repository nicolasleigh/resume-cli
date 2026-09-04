"""pdf_service 测试:文件校验与文本提取。"""

import pytest

from resume_cli.errors import (
    EmptyPDFError,
    NotPDFError,
    PDFNotFoundError,
    PDFReadError,
    PathIsNotFileError,
)
from resume_cli.pdf_service import extract_text, validate_pdf_file


def test_validate_missing_file(tmp_path):
    path = tmp_path / "not-exist.pdf"
    with pytest.raises(PDFNotFoundError):
        validate_pdf_file(path)


def test_validate_directory(tmp_path):
    with pytest.raises(PathIsNotFileError):
        validate_pdf_file(tmp_path)


def test_validate_wrong_extension(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(NotPDFError):
        validate_pdf_file(path)


def test_validate_fake_pdf(tmp_path):
    # 后缀是 .pdf 但内容是纯文本,应被解析器打开检查识破。
    path = tmp_path / "fake.pdf"
    path.write_bytes(b"this is definitely not a pdf")
    with pytest.raises(PDFReadError):
        validate_pdf_file(path)


def test_extract_text_pdf(text_pdf):
    text = extract_text(text_pdf)
    assert "Zhang San" in text
    assert "Skills" in text
    assert "Experience" in text


def test_extract_blank_pdf_raises(blank_pdf):
    with pytest.raises(EmptyPDFError):
        extract_text(blank_pdf)
