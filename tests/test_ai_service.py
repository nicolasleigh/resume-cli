"""ai_service 测试:本地 Ollama(OpenAI 兼容)场景允许缺 API Key。"""

import pytest

from resume_cli.ai_service import AIClient
from resume_cli.errors import AIConfigError


@pytest.fixture(autouse=True)
def _no_dotenv(monkeypatch):
    # 测试时不加载真实 .env,保证环境变量完全由 monkeypatch 控制,避免本地配置干扰。
    monkeypatch.setattr("resume_cli.ai_service.load_dotenv", lambda: None)


def test_local_base_url_allows_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OPENAI_MODEL", "llama3.1:8b")
    client = AIClient()
    assert client.api_key == "ollama"  # 本地服务不校验 Key,填占位符
    assert client.model == "llama3.1:8b"


def test_remote_base_url_without_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    with pytest.raises(AIConfigError):
        AIClient()


def test_no_config_without_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    with pytest.raises(AIConfigError):
        AIClient()
