"""resume-cli 命令行入口。

Phase 0 目标:让 `resume-cli --help` 能展示 parse / extract / score 三个命令。
三个命令在本阶段只是占位,具体实现将在后续 Phase 逐步完成。
"""

from pathlib import Path

import typer

from resume_cli.ai_service import AIClient
from resume_cli.errors import ResumeCliError
from resume_cli.extract_prompt import SYSTEM_PROMPT, build_extract_user_message
from resume_cli.json_utils import validate_resume_json
from resume_cli.pdf_service import extract_text

app = typer.Typer(
    name="resume-cli",
    help="AI Resume Parser CLI: parse a PDF resume, extract structured info, score against a JD.",
    no_args_is_help=True,
)


@app.command()
def parse(pdf_path: Path) -> None:
    """Read a PDF resume and extract plain text."""
    try:
        # extract_text 内部会先做文件校验,再提取全文,一条链路完成
        # 文件不存在/是目录/非 PDF/无法读取/无文本 五类错误处理。
        text = extract_text(pdf_path)
    except ResumeCliError as e:
        # 预期内的业务错误统一转成一行 "Error: ..." 输出到 stderr,
        # 并以非 0 退出码结束,而不是把 Python traceback 展示给用户。
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # 成功:直接把简历全文输出到 stdout(供管道/重定向使用)。
    typer.echo(text)


@app.command()
def extract(pdf_path: Path) -> None:
    """Extract structured candidate information using AI."""
    try:
        # 1~6:PDF 校验 + 提取全文(空文本会抛 EmptyPDFError)。
        resume_text = extract_text(pdf_path)
        # 7~9:构造 Prompt 并调用 AI,拿到模型返回文本。
        client = AIClient()
        ai_text = client.chat(SYSTEM_PROMPT, build_extract_user_message(resume_text))
        # 10~12:解析 JSON、四层校验 Schema、转成 Resume 模型。
        resume = validate_resume_json(ai_text)
    except ResumeCliError as e:
        # 配置缺失 / 网络错误 / 返回非法 JSON 等统一转成友好错误。
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # 13:以缩进、UTF-8、中文原样显示的格式输出 JSON。
    typer.echo(resume.model_dump_json(indent=2, ensure_ascii=False))


@app.command()
def score(pdf_path: Path, jd: Path) -> None:
    """Score candidate against a job description using AI."""
    # 占位实现:正式实现在后续 Phase(JD 读取 + Score 模型)完成。
    typer.echo("score 命令将在后续阶段实现。", err=True)
    raise typer.Exit(code=1)

def main() -> None:
    """setuptools console script 入口:直接运行 Typer app。"""
    app()
