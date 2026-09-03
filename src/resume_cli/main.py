"""resume-cli 命令行入口。

Phase 0 目标:让 `resume-cli --help` 能展示 parse / extract / score 三个命令。
三个命令在本阶段只是占位,具体实现将在后续 Phase 逐步完成。
"""

from pathlib import Path

import typer

app = typer.Typer(
    name="resume-cli",
    help="AI Resume Parser CLI: parse a PDF resume, extract structured info, score against a JD.",
    no_args_is_help=True,
)


@app.command()
def parse(pdf_path: Path) -> None:
    """Read a PDF resume and extract plain text."""
    # 占位实现:正式实现在后续 Phase(文件校验 + PDF 文本提取)完成。
    typer.echo("parse 命令将在后续阶段实现。", err=True)
    raise typer.Exit(code=1)


@app.command()
def extract(pdf_path: Path) -> None:
    """Extract structured candidate information using AI."""
    # 占位实现:正式实现在后续 Phase(Resume 模型 + AI Client)完成。
    typer.echo("extract 命令将在后续阶段实现。", err=True)
    raise typer.Exit(code=1)


@app.command()
def score(pdf_path: Path, jd: Path) -> None:
    """Score candidate against a job description using AI."""
    # 占位实现:正式实现在后续 Phase(JD 读取 + Score 模型)完成。
    typer.echo("score 命令将在后续阶段实现。", err=True)
    raise typer.Exit(code=1)

def main() -> None:
    """setuptools console script 入口:直接运行 Typer app。"""
    app()
