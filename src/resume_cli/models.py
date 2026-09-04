"""resume-cli 的 Pydantic 数据模型。

为什么用 Pydantic 而不是普通 dict:
- AI 返回的是 JSON,直接以 dict 传递无法保证字段存在、类型正确;
- 用模型定义字段类型,解析时自动校验/填充,业务代码拿到的是结构清晰的对象;
- 后续 --output 直接调用 model_dump_json() 即可输出规范 JSON。
"""

from pydantic import BaseModel, Field


class Education(BaseModel):
    """一段教育经历。

    每项都是可空字符串:简历中某段教育经历若缺少专业或毕业时间,
    置为 None 而不是由 AI 猜测(需求 §16:缺失字段不臆造)。
    """

    school: str | None = None
    major: str | None = None
    degree: str | None = None
    graduation_time: str | None = None


class Resume(BaseModel):
    """从简历文本中抽取出的结构化候选人信息(需求 §10)。"""

    name: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    # 教育经历可能有多段,缺省为空列表。
    education: list[Education] = Field(default_factory=list)
    # 技能列表,每一项是技能名称字符串。
    skills: list[str] = Field(default_factory=list)
