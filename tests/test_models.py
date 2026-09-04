"""数据模型测试:Resume 与 Score(§36 Test 2/3)。"""

import pytest
from pydantic import ValidationError

from resume_cli.models import Resume, Score


def test_resume_valid_dict():
    raw = {
        "name": "Zhang San",
        "phone": "13800138000",
        "email": "test@example.com",
        "city": "Beijing",
        "education": [
            {"school": "Peking University", "major": "CS", "degree": "Bachelor", "graduation_time": "2020"}
        ],
        "skills": ["Python", "Go"],
    }
    resume = Resume.model_validate(raw)
    assert resume.name == "Zhang San"
    assert resume.education[0].school == "Peking University"
    assert resume.skills == ["Python", "Go"]


def test_resume_empty_defaults():
    # 空输入:所有字段按规则缺省为 null / [],不臆造。
    resume = Resume()
    assert resume.name is None
    assert resume.phone is None
    assert resume.email is None
    assert resume.city is None
    assert resume.education == []
    assert resume.skills == []


def test_score_valid():
    score = Score.model_validate(
        {
            "overall_score": 82,
            "skill_score": 88,
            "experience_score": 80,
            "education_score": 75,
            "comment": "基础扎实",
            "interview_questions": ["q1", "q2"],
        }
    )
    assert score.overall_score == 82
    assert len(score.interview_questions) == 2


@pytest.mark.parametrize("field,value", [("overall_score", 120), ("overall_score", -10)])
def test_score_out_of_range_rejected(field, value):
    base = {
        "skill_score": 88,
        "experience_score": 80,
        "education_score": 75,
        "comment": "x",
        "interview_questions": ["q"],
    }
    base[field] = value
    with pytest.raises(ValidationError):
        Score.model_validate(base)


def test_score_missing_fields_rejected():
    # 只给部分字段,缺字段必须校验失败(§23)。
    with pytest.raises(ValidationError):
        Score(overall_score=82)
