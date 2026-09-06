"""resume-cli 命令行入口。

提供三个子命令:
- parse:读取 PDF 简历并输出纯文本;
- extract:用 AI 抽取结构化候选人信息(JSON);
- score:结合 JD 用 AI 输出匹配评分(JSON)。

所有可预期的错误统一转成 "Error: ..." 友好提示;完整错误体系见 errors.py。
"""

from pathlib import Path

import typer

from resume_cli.ai_service import AIClient
from resume_cli.errors import ResumeCliError
from resume_cli.extract_prompt import SYSTEM_PROMPT, build_extract_user_message
from resume_cli.jd_service import read_jd_text
from resume_cli.json_utils import validate_resume_json, validate_score_json
from resume_cli.logger import logger
from resume_cli.mock_ai import mock_extract_response, mock_score_response
from resume_cli.pdf_service import extract_text
from resume_cli.score_prompt import (
    SYSTEM_PROMPT as SCORE_SYSTEM_PROMPT,
    build_score_user_message,
)

app = typer.Typer(
    name="resume-cli",
    help="AI Resume Parser CLI: parse a PDF resume, extract structured info, score against a JD.",
    no_args_is_help=True,
)


def _emit_json(payload: str, output: Path | None) -> None:
    """统一处理结果输出(需求 §30)。

    - 未传 --output:完整 JSON 直接打印到 stdout;
    - 传了 --output:完整 JSON 写入文件,终端只显示保存位置的简要提示。
    """
    if output is None:
        typer.echo(payload)
        return
    output.write_text(payload + "\n", encoding="utf-8")
    typer.echo("Result saved to:")
    typer.echo(str(output))


@app.command()
def parse(pdf_path: Path) -> None:
    """Read a PDF resume and extract plain text."""
    try:
        logger.info("Reading PDF")
        # extract_text 内部会先做文件校验,再提取全文,一条链路完成
        # 文件不存在/是目录/非 PDF/无法读取/无文本 五类错误处理。
        text = extract_text(pdf_path)
        # 只记录字符数,不输出全文,避免日志泄露候选人隐私(§31)。
        logger.info("Extracted %d characters", len(text))
    except ResumeCliError as e:
        # 预期内的业务错误统一转成一行 "Error: ..." 输出到 stderr,
        # 并以非 0 退出码结束,而不是把 Python traceback 展示给用户。
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # 成功:直接把简历全文输出到 stdout(供管道/重定向使用)。
    logger.info("Done")
    typer.echo(text)


@app.command()
def extract(
    pdf_path: Path,
    mock: bool = typer.Option(False, "--mock", help="Use mock AI responses (no API key required)."),
    output: Path | None = typer.Option(
        None, "--output", help="Save the full JSON result to this file."
    ),
) -> None:
    """Extract structured candidate information using AI."""
    try:
        # 1~6:PDF 校验 + 提取全文(空文本会抛 EmptyPDFError)。
        logger.info("Reading PDF")
        resume_text = extract_text(pdf_path)
        logger.info("Extracted %d characters", len(resume_text))
        # 7~9:构造 Prompt 并调用 AI;--mock 时跳过真实调用,直接用固定响应,
        # 让没有 API Key 的环境也能完整演示(需求 §27)。
        if mock:
            logger.info("Using mock AI response")
            ai_text = mock_extract_response()
        else:
            client = AIClient()
            # 只记录模型名,不打印 API Key / base_url(§31)。
            logger.info("Calling AI model: %s", client.model)
            ai_text = client.chat(SYSTEM_PROMPT, build_extract_user_message(resume_text))
        # 10~12:解析 JSON、四层校验 Schema、转成 Resume 模型。
        logger.info("Validating response")
        resume = validate_resume_json(ai_text)
    except ResumeCliError as e:
        # 配置缺失 / 网络错误 / 返回非法 JSON 等统一转成友好错误。
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # 13:以缩进、UTF-8、中文原样显示的格式输出 JSON。
    logger.info("Done")
    payload = resume.model_dump_json(indent=2)
    _emit_json(payload, output)


@app.command()
def score(
    pdf_path: Path,
    jd: Path = typer.Option(..., "--jd", help="Path to the job description text file."),
    mock: bool = typer.Option(False, "--mock", help="Use mock AI responses (no API key required)."),
    output: Path | None = typer.Option(
        None, "--output", help="Save the full JSON result to this file."
    ),
) -> None:
    """Score candidate against a job description using AI."""
    try:
        # 1~2:PDF 校验 + 提取全文(流程对应需求 §21)。
        logger.info("Reading PDF")
        resume_text = extract_text(pdf_path)
        logger.info("Extracted %d characters", len(resume_text))
        # 3~4:JD 校验 + 读取全文。
        logger.info("Reading JD")
        jd_text = read_jd_text(jd)
        # 5~6:构造评分 Prompt 并调用 AI;--mock 时跳过真实调用。
        if mock:
            logger.info("Using mock AI response")
            ai_text = mock_score_response()
        else:
            client = AIClient()
            logger.info("Calling AI model: %s", client.model)
            ai_text = client.chat(
                SCORE_SYSTEM_PROMPT, build_score_user_message(resume_text, jd_text)
            )
        # 7~9:解析 JSON、校验评分结果(分数 0~100 由模型保证)。
        logger.info("Validating response")
        score_result = validate_score_json(ai_text)
    except ResumeCliError as e:
        # PDF/JD/配置/网络/返回格式错误统一转成友好错误。
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # 10:输出规范 JSON(--output 时写入文件)。
    logger.info("Done")
    payload = score_result.model_dump_json(indent=2, ensure_ascii=False)
    _emit_json(payload, output)


def main() -> None:
    """setuptools console script 入口:直接运行 Typer app。"""
    try:
        app()
    except Exception as exc:  # noqa: BLE001 - 兜底,避免把 traceback 抛给普通用户
        # 各命令已把可预期的业务错误转为友好提示;此处只兜底"未预期异常",
        # 保证普通用户在任何情况下都不会看到 Python traceback(需求 §34)。
        typer.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
