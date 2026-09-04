"""统一 AI 调用层(Phase 5)。

为什么单独封装一层(需求 §11):
- 业务代码(extract / score)不应到处直接调用 OpenAI SDK,
  所有调用统一收敛到 AIClient;
- 环境变量读取、缺失 API Key 报错、网络 / 超时 / API 错误转换,
  都在这一层完成,上层只需拿到文本回复或捕获友好的 ResumeCliError。
"""

import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
)

from resume_cli.errors import AIConfigError, AIRequestError, AIResponseError

# 未显式配置 OPENAI_MODEL 时使用的默认模型。
DEFAULT_MODEL = "gpt-4o-mini"

# 本地 host:当 base_url 指向本地时,认为用户在跑 Ollama 之类的本地模型,
# 这类服务通常不校验 API Key(见 __init__ 的处理)。
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _is_local_base_url(base_url: str | None) -> bool:
    """判断 base_url 是否指向本机(用于本地 Ollama 场景)。"""
    if not base_url:
        return False
    host = urlparse(base_url).hostname or ""
    return host in _LOCAL_HOSTS


class AIClient:
    """对 OpenAI 兼容 API 的极简封装。"""

    def __init__(self) -> None:
        # 读取项目根目录下的 .env(若存在)。
        # load_dotenv 默认不会覆盖已存在的环境变量,因此命令行导出的变量优先。
        load_dotenv()

        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL") or None
        self.model = os.getenv("OPENAI_MODEL") or DEFAULT_MODEL

        if not self.api_key:
            if _is_local_base_url(self.base_url):
                # 本地 Ollama 兼容服务不校验 Key,填占位符即可让 SDK 正常构造。
                self.api_key = "ollama"
            else:
                # 没有 Key 且不是本地服务时提前给出可操作提示,
                # 而不是等 SDK 抛晦涩错误。
                raise AIConfigError(
                    "OPENAI_API_KEY is not configured.\n"
                    "Please set the environment variable before using extract.\n"
                    "Hint: copy .env.example to .env and fill in your key, "
                    "or use --mock to run the demo without an API key.\n"
                    "Local Ollama? set OPENAI_BASE_URL=http://localhost:11434/v1 "
                    "(no API key required)."
                )

        # base_url 为空则使用 OpenAI 官方地址;若配置了兼容网关则走网关。
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """发送一轮 system + user 对话,返回模型文本回复。

        网络错误、超时、API 错误统一转成 AIRequestError,
        避免把 SDK 底层异常直接抛给 CLI 用户。
        """
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                # 结构化抽取/评分希望结果稳定,关闭随机性。
                temperature=0,
            )
        except (APIConnectionError, APITimeoutError, APIStatusError) as exc:
            raise AIRequestError(
                "Failed to call AI API.\n"
                "Please check your API key and network connection."
            ) from exc

        # content 理论上始终存在;为空时给出明确错误,避免下层解析出晦涩异常。
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            raise AIResponseError("AI returned an empty response.")
        return content
