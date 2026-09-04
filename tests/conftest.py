"""pytest 共享 fixture。

测试需要"可提取文本的 PDF"与"空白 PDF",最可靠的方式是复用
examples/generate_sample_pdfs.py 里的极简 PDF 构造器在临时目录生成,
而不是依赖仓库里是否存在示例 PDF 文件。
"""

import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
# examples 不是 Python 包,这里把目录加入 sys.path 以便直接 import 该脚本。
sys.path.insert(0, str(EXAMPLES_DIR))

import generate_sample_pdfs as pdfgen  # noqa: E402


@pytest.fixture
def text_pdf(tmp_path):
    """一份两页、含可提取文本的 PDF。"""
    path = tmp_path / "resume.pdf"
    path.write_bytes(pdfgen._build_pdf([pdfgen.RESUME_PAGE_1, pdfgen.RESUME_PAGE_2]))
    return path


@pytest.fixture
def blank_pdf(tmp_path):
    """一页没有任何文字的 PDF(用于空文本判断)。"""
    path = tmp_path / "blank.pdf"
    path.write_bytes(pdfgen._build_pdf([[]]))
    return path


@pytest.fixture
def jd_file(tmp_path):
    """一份合法的 JD 文本文件。"""
    path = tmp_path / "jd.txt"
    path.write_text(
        "岗位:AI 全栈开发工程师\n岗位要求:\n1. 熟悉 Python\n2. 熟悉 FastAPI\n",
        encoding="utf-8",
    )
    return path
