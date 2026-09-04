"""JD(岗位描述)文件读取服务(Phase 8)。

score 命令评分前需要读取 JD 文本;这里集中处理 JD 输入的三种错误:
文件不存在 / 路径不是普通文件 / 内容为空。
"""

from pathlib import Path

from resume_cli.errors import (
    JDEmptyError,
    JDNotFoundError,
    PathIsNotFileError,
)


def read_jd_text(jd_path: Path) -> str:
    """读取 JD 文本文件并返回内容(去掉首尾空白),非法输入抛对应错误。"""
    if not jd_path.exists():
        raise JDNotFoundError(f"JD file does not exist:\n{jd_path}")

    if not jd_path.is_file():
        raise PathIsNotFileError("JD path is not a file")

    # 空 JD 没有评分意义,因此在调用 AI 之前直接拒绝(需求 §19)。
    content = jd_path.read_text(encoding="utf-8").strip()
    if not content:
        raise JDEmptyError("JD file is empty")

    return content
