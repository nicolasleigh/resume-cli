"""AI 返回 JSON 的解析与校验工具(Phase 6)。

为什么需要这里(需求 §17):
- AI 返回的内容不能直接信任,必须先做格式解析与结构校验;
- 模型经常在 JSON 外加 ```json 围栏或说明文字,这里负责剥掉它们;
- 校验失败时抛 AIResponseError,由命令入口统一转成友好的错误信息。
"""

import json
from typing import Any

from pydantic import ValidationError

from resume_cli.errors import AIResponseError
from resume_cli.models import Resume, Score

# extract schema 要求顶层包含这六个字段。
REQUIRED_TOP_KEYS = {"name", "phone", "email", "city", "education", "skills"}
# 每条教育经历要求包含这四个字段。
EDUCATION_FIELDS = {"school", "major", "degree", "graduation_time"}
# score schema 要求顶层包含这六个字段。
SCORE_REQUIRED_KEYS = {
    "overall_score",
    "skill_score",
    "experience_score",
    "education_score",
    "comment",
    "interview_questions",
}


def parse_json(text: str) -> Any:
    """把模型返回的文本解析成 Python 对象。

    先尝试整段直接解析;若失败(说明带了围栏/散文),
    再尝试截取从第一个 { 到最后一个 }(或 [ 到 ])的子串解析。
    全部失败则抛 AIResponseError。
    """
    stripped = text.strip()
    if not stripped:
        raise AIResponseError("AI response is empty.")

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    for start_ch, end_ch in (("{", "}"), ("[", "]")):
        start = stripped.find(start_ch)
        end = stripped.rfind(end_ch)
        if start != -1 and end > start:
            candidate = stripped[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    raise AIResponseError("AI response is not valid JSON.")


def validate_resume_json(raw_text: str) -> Resume:
    """四层校验(需求 §17)并把合法结果转成 Resume 模型。

    第一层:是合法 JSON(parse_json);
    第二层:顶层必须是对象且包含全部六个字段;
    第三层:education / skills 必须是数组;
    第四层:education 每个元素必须是对象且含四个字段。
    """
    data = parse_json(raw_text)

    if not isinstance(data, dict):
        raise AIResponseError("AI response JSON is not an object.")

    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        raise AIResponseError(
            "AI response is missing fields: " + ", ".join(sorted(missing))
        )

    if not isinstance(data["education"], list) or not isinstance(data["skills"], list):
        raise AIResponseError("fields 'education' and 'skills' must be arrays.")

    for index, edu in enumerate(data["education"]):
        if not isinstance(edu, dict):
            raise AIResponseError(f"education[{index}] is not an object.")
        missing = EDUCATION_FIELDS - edu.keys()
        if missing:
            raise AIResponseError(
                f"education[{index}] is missing fields: " + ", ".join(sorted(missing))
            )

    # 字段类型(如 name 必须是 str|null、skills 元素必须是 str)交给 Pydantic 兜底。
    try:
        return Resume.model_validate(data)
    except ValidationError as exc:
        raise AIResponseError(f"AI response schema is invalid: {exc}") from exc


def validate_score_json(raw_text: str) -> Score:
    """校验评分结果 JSON 并转成 Score 模型。

    检查思路同 validate_resume_json:
    合法 JSON → 顶层对象 → 六个字段齐全 → interview_questions 是数组;
    分数范围(0~100)与类型由 Score 模型的 Field(ge=0, le=100)兜底。
    """
    data = parse_json(raw_text)

    if not isinstance(data, dict):
        raise AIResponseError("AI response JSON is not an object.")

    missing = SCORE_REQUIRED_KEYS - data.keys()
    if missing:
        raise AIResponseError(
            "AI response is missing fields: " + ", ".join(sorted(missing))
        )

    if not isinstance(data["interview_questions"], list):
        raise AIResponseError("field 'interview_questions' must be an array.")

    try:
        return Score.model_validate(data)
    except ValidationError as exc:
        raise AIResponseError(f"AI response schema is invalid: {exc}") from exc
