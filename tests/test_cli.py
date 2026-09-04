"""CLI 端到端测试(不含真实网络;Mock 覆盖 AI 环节,§36 Test 5)。"""

from typer.testing import CliRunner

from resume_cli.main import app

runner = CliRunner()


def test_parse_success(text_pdf):
    result = runner.invoke(app, ["parse", str(text_pdf)])
    assert result.exit_code == 0
    assert "Zhang San" in result.output


def test_parse_missing_file():
    result = runner.invoke(app, ["parse", "no-such-file.pdf"])
    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_extract_mock_runs(text_pdf):
    result = runner.invoke(app, ["extract", str(text_pdf), "--mock"])
    assert result.exit_code == 0
    assert '"name": "张三"' in result.output
    assert "education" in result.output


def test_extract_mock_blank_pdf_errors(blank_pdf):
    result = runner.invoke(app, ["extract", str(blank_pdf), "--mock"])
    assert result.exit_code == 1
    assert "no extractable text" in result.output


def test_score_mock_runs(text_pdf, jd_file):
    result = runner.invoke(app, ["score", str(text_pdf), "--jd", str(jd_file), "--mock"])
    assert result.exit_code == 0
    assert '"overall_score": 82' in result.output
    assert "comment" in result.output
