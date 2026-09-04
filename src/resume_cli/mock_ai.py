"""Mock AI 响应(Phase 12)。

为什么需要 Mock 模式(需求 §27):
- 没有 OPENAI_API_KEY 或网络受限时,也要能完整演示 extract / score 流程;
- Mock 返回固定但合法的 JSON,后续依然走"解析 → 校验 → 模型 → 输出",
  因此演示的真实代码路径与真实 AI 调用只有"是否联网"这一处差异。
"""

# 与需求文档 §27 示例一致的固定简历 JSON。
MOCK_EXTRACT_JSON = """{
  "name": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "city": "北京",
  "education": [
    {
      "school": "北京大学",
      "major": "计算机科学",
      "degree": "本科",
      "graduation_time": "2020"
    }
  ],
  "skills": ["Python", "Go", "FastAPI", "PostgreSQL"]
}"""

# 固定的评分 JSON:覆盖 overall/skill/experience/education 与 comment/面试题。
MOCK_SCORE_JSON = """{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人具备较好的全栈开发基础,技能与岗位要求较匹配,但缺少明确的大模型应用经验。",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目。",
    "你是否有调用大模型 API 的实际经验?"
  ]
}"""


def mock_extract_response() -> str:
    """返回固定的 extract 模型输出(JSON 字符串)。"""
    return MOCK_EXTRACT_JSON


def mock_score_response() -> str:
    """返回固定的 score 模型输出(JSON 字符串)。"""
    return MOCK_SCORE_JSON
