# resume-cli

AI 简历解析 CLI Demo:读取本地 PDF 简历 → 提取文本 → 调用大模型抽取结构化候选人信息 → 读取岗位描述(JD)→ 大模型匹配评分 → 以清晰的 JSON 输出到终端。

这是一个「可安装、可运行、可演示、可测试」的招聘辅助 AI CLI 示例项目,定位为 **Demo**,不会扩展成完整招聘系统。

## 1. 项目简介

- **解决的问题**:从 PDF 简历和岗位描述中,自动抽出候选人结构化信息并给出匹配评分;
- **核心链路**:

```text
PDF 简历 → parse → 简历文本 → extract → 结构化候选人信息(JSON)
                                               ↑
JD 文件 → score → 匹配评分(JSON)
```

## 2. 功能列表

```text
[x] PDF 文本提取(遍历全部页面拼接)
[x] 输入校验(文件不存在 / 目录 / 非 PDF / 无法读取 / 无文本)
[x] AI 简历信息抽取(extract)
[x] JD 文件读取与校验
[x] JD 匹配评分(score)
[x] Mock AI(--mock,无 API Key 可完整演示)
[x] JSON 输出(缩进 / UTF-8 / 中文原样)
[x] --output 把结果写入文件
[x] 基础 JSON 自动修复(剥离代码围栏与说明文字)
[x] 日志(INFO 输出到 stderr,不泄露 Key 与隐私)
[x] pytest 测试
```

## 3. 技术选型

| 技术 | 用途 |
| --- | --- |
| Python 3.11+ | 语言 |
| Typer | 命令行框架(解析/提取/评分三个子命令) |
| pypdf | 从 PDF 提取文本 |
| OpenAI Python SDK | 调用大模型(兼容 OpenAI 协议的服务) |
| Pydantic | 数据模型与 JSON Schema 校验 |
| python-dotenv | 读取 `.env` 环境变量 |
| pytest | 单元与端到端测试 |

## 4. 项目结构

```text
resume-cli/
├── README.md
├── pyproject.toml            # 项目元数据、依赖、resume-cli 入口
├── .env.example              # 环境变量示例(复制为 .env 使用)
├── .gitignore
├── src/resume_cli/
│   ├── __init__.py
│   ├── main.py               # Typer CLI 入口(parse / extract / score)
│   ├── errors.py             # 统一异常体系(ResumeCliError 及子类)
│   ├── pdf_service.py        # PDF 校验 + 文本提取
│   ├── jd_service.py         # JD 文件读取与校验
│   ├── ai_service.py         # AIClient:OpenAI 调用层
│   ├── models.py             # Pydantic 模型(Resume / Education / Score)
│   ├── extract_prompt.py     # extract 的 system prompt
│   ├── score_prompt.py       # score 的 system prompt
│   ├── json_utils.py         # AI 返回 JSON 的解析与 Schema 校验
│   ├── mock_ai.py            # Mock 模式的固定响应
│   └── logger.py             # stderr 日志
├── tests/
│   ├── conftest.py           # 生成测试用 PDF/JD fixture
│   └── test_*.py             # 服务/模型/JSON/CLI 测试
└── examples/
    ├── generate_sample_pdfs.py  # 生成演示 PDF 的脚本(纯标准库)
    ├── resume.pdf            # 虚拟简历(示例)
    ├── blank.pdf             # 空白 PDF(演示无文本错误)
    └── jd.txt                # 虚拟岗位描述
```

## 5. 环境要求

```text
Python >= 3.11
```

> macOS 系统自带的 Python 可能是 3.9,请使用 Homebrew 等安装的新版本,
> 例如 `/opt/homebrew/bin/python3.12`。

## 6. 安装

```bash
cd resume-cli
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

安装后即可使用:

```bash
.venv/bin/resume-cli --help
```

首次演示前生成示例 PDF(纯标准库,无需联网):

```bash
.venv/bin/python examples/generate_sample_pdfs.py
```

> 生成的 `examples/resume.pdf`(两页虚拟简历)与 `examples/blank.pdf`(空白 PDF)用于下面的示例。

## 7. 环境变量

`resume-cli` 通过环境变量读取 AI 配置。复制 `.env.example` 为 `.env` 并填写即可:

```bash
cp .env.example .env
```

| 变量 | 说明 | 必填 |
| --- | --- | --- |
| `OPENAI_API_KEY` | API Key | 是(除非用 `--mock`) |
| `OPENAI_BASE_URL` | 兼容 OpenAI 协议的网关地址(可选) | 否 |
| `OPENAI_MODEL` | 模型名,默认 `gpt-4o-mini` | 否 |

> `.env` 已被 `.gitignore` 忽略,**不要把真实 API Key 提交到 GitHub**。
> 没有 Key 时请使用 `--mock` 模式(见下文)。

## 8. parse 使用方式

读取 PDF 并输出纯文本:

```bash
resume-cli parse ./examples/resume.pdf
```

示例输出(实际排版以终端为准):

```text
Zhang San
13800138000
zhangsan@example.com

Education
Peking University
Computer Science
Bachelor
2016 - 2020
Skills
Python, Go, FastAPI, PostgreSQL, React

Experience
Backend Engineer at Example Corp
Built a RAG service with Python and FastAPI
Designed PostgreSQL schemas for AI features
```

错误示例(exit code 非 0):

```text
$ resume-cli parse ./not-exist.pdf
Error: PDF file does not exist:
not-exist.pdf
```

## 9. extract 使用方式

抽取结构化候选人信息:

```bash
resume-cli extract ./examples/resume.pdf
```

使用 Mock 模式(无需 API Key):

```bash
resume-cli extract ./examples/resume.pdf --mock
```

示例输出(JSON,缩进 / UTF-8 / 中文原样):

```json
{
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
}
```

将完整 JSON 保存到文件(终端只提示保存位置):

```bash
resume-cli extract ./examples/resume.pdf --mock --output result.json
```

## 10. score 使用方式

根据 JD 对候选人评分:

```bash
resume-cli score ./examples/resume.pdf --jd ./examples/jd.txt
```

Mock 模式:

```bash
resume-cli score ./examples/resume.pdf --jd ./examples/jd.txt --mock
```

示例输出:

```json
{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人具备较好的全栈开发基础,技能与岗位要求较匹配,但缺少明确的大模型应用经验。",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目。",
    "你是否有调用大模型 API 的实际经验?"
  ]
}
```

同样支持 `--output`:

```bash
resume-cli score ./examples/resume.pdf --jd ./examples/jd.txt --mock --output score.json
```

## 11. Mock 模式

```bash
resume-cli extract ./examples/resume.pdf --mock
resume-cli score ./examples/resume.pdf --jd ./examples/jd.txt --mock
```

Mock 模式不需要 AI API Key,可以用于本地测试和演示。它返回固定的合法 JSON,
但仍会走「解析 → 校验 → 模型 → 输出」的真实代码路径;与真实 AI 调用仅差「是否联网」一处。

## 12. 测试

```bash
.venv/bin/pytest -q
```

预期输出:

```text
31 passed
```

## 13. 已知问题

1. **暂不支持 OCR**:只支持能直接提取文本的 PDF;纯扫描图片型 PDF 会提示
   `PDF contains no extractable text`,MVP 不实现 OCR。
2. **AI 输出依赖模型质量**:结构化抽取/评分由大模型生成,不同模型质量会有差异;
   本项目对返回结果做了 JSON 解析与 Schema 校验以降低影响,但无法保证 100% 正确。
3. **评分属于 AI 辅助评分**:不代表真实招聘决策,仅供演示。
4. **Mock 输出为固定示例数据**:`--mock` 返回的内容与输入简历文本无关,仅用于演示流程。

## 其它

- 示例 PDF 由 `examples/generate_sample_pdfs.py` 生成(内容为 ASCII 的虚拟简历,
  避免使用真实候选人信息)。如需演示真实中文简历,可用 Word/WPS 导出 PDF 后替换 `examples/resume.pdf`。
- CLI 帮助:`resume-cli --help`、`resume-cli parse --help`、`resume-cli extract --help`、`resume-cli score --help`。
