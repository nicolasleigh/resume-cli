"""json_utils 测试:围栏解析 + resume/score 校验。"""

import pytest

from resume_cli.errors import AIResponseError
from resume_cli.json_utils import (
    parse_json,
    validate_resume_json,
    validate_score_json,
)

VALID_RESUME = """{
  "name": "Zhang San",
  "phone": "13800138000",
  "email": "test@example.com",
  "city": "Beijing",
  "education": [
    {"school": "Peking University", "major": "CS", "degree": "Bachelor", "graduation_time": "2020"}
  ],
  "skills": ["Python", "Go"]
}"""

VALID_SCORE = """{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "基础较匹配",
  "interview_questions": ["q1", "q2"]
}"""


def test_parse_json_with_code_fence():
    raw = '```json\n{"name": "Zhang San"}\n```'
    assert parse_json(raw) == {"name": "Zhang San"}


def test_parse_json_with_prose():
    raw = 'Here is the result:\n{"skills": ["Python"]}'
    assert parse_json(raw) == {"skills": ["Python"]}


def test_parse_json_invalid_raises():
    with pytest.raises(AIResponseError):
        parse_json("no json here at all")


def test_validate_resume_valid():
    resume = validate_resume_json(VALID_RESUME)
    assert resume.name == "Zhang San"


def test_validate_resume_missing_keys_raises():
    with pytest.raises(AIResponseError):
        validate_resume_json('{"name": "x"}')


def test_validate_resume_education_not_list_raises():
    raw = '{"name":"x","phone":null,"email":null,"city":null,"education":{},"skills":[]}'
    with pytest.raises(AIResponseError):
        validate_resume_json(raw)


def test_validate_score_valid():
    score = validate_score_json(VALID_SCORE)
    assert score.overall_score == 82


def test_validate_score_out_of_range_raises():
    raw = '{"overall_score":120,"skill_score":88,"experience_score":80,"education_score":75,"comment":"x","interview_questions":["q"]}'
    with pytest.raises(AIResponseError):
        validate_score_json(raw)


def test_validate_score_missing_keys_raises():
    with pytest.raises(AIResponseError):
        validate_score_json('{"overall_score": 82}')
