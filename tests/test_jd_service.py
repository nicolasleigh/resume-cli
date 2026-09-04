"""jd_service 测试:JD 文件读取与空内容判断(§36 Test 4)。"""

import pytest

from resume_cli.errors import JDEmptyError, JDNotFoundError, PathIsNotFileError
from resume_cli.jd_service import read_jd_text


def test_jd_missing(tmp_path):
    with pytest.raises(JDNotFoundError):
        read_jd_text(tmp_path / "not-exist.txt")


def test_jd_is_directory(tmp_path):
    with pytest.raises(PathIsNotFileError):
        read_jd_text(tmp_path)


def test_jd_empty(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    with pytest.raises(JDEmptyError):
        read_jd_text(path)


def test_jd_whitespace_only(tmp_path):
    path = tmp_path / "blank.txt"
    path.write_text("  \n\t ", encoding="utf-8")
    with pytest.raises(JDEmptyError):
        read_jd_text(path)


def test_jd_valid(jd_file):
    content = read_jd_text(jd_file)
    assert content.startswith("岗位:")
    assert "Python" in content
