# resume-cli 常用命令入口(锦上添花)。
# 用法示例:
#   make install        # 创建 .venv 并安装(含 dev 依赖)
#   make test           # 运行 pytest
#   make demo           # 依次演示 parse / extract --mock / score --mock

PYTHON     ?= python
RESUME_CLI ?= resume-cli
PDF        ?= examples/cv.pdf
MOCK_PDF    ?= examples/resume.pdf
JD         ?= examples/jd.txt
CV_PARSE   ?= examples/cv_parse.txt
CV_EXTRACT ?= examples/cv_extract.txt
CV_SCORE   ?= examples/cv_score.txt

.PHONY: help install generate-examples test demo parse extract score

help:
	@echo "可用目标:"
	@echo "  make install            创建 .venv 并安装依赖(含 dev)"
	@echo "  make generate-examples  生成 examples/resume.pdf 与 blank.pdf"
	@echo "  make test               运行 pytest"
	@echo "  make demo               依次演示 parse / extract / score"
	@echo "  make parse              运行 resume-cli parse examples/cv.pdf"
	@echo "  make extract            运行 resume-cli extract examples/cv.pdf"
	@echo "  make score              运行 resume-cli score examples/cv.pdf --jd examples/jd.txt"

install:
	python3.12 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

generate-examples:
	$(PYTHON) examples/generate_sample_pdfs.py

test:
	$(PYTHON) -m pytest -q

demo:
	$(RESUME_CLI) parse $(PDF)
	@echo "=================================="
	$(RESUME_CLI) extract $(PDF)
	@echo "=================================="
	$(RESUME_CLI) score $(PDF) --jd $(JD)

demo-save-to-file:
	$(RESUME_CLI) parse $(PDF)
	@echo "=================================="
	$(RESUME_CLI) extract $(PDF) --output $(CV_EXTRACT)
	@echo "=================================="
	$(RESUME_CLI) score $(PDF) --jd $(JD) --output $(CV_SCORE)

demo-mock: generate-examples
	$(RESUME_CLI) parse $(MOCK_PDF)
	@echo "=================================="
	$(RESUME_CLI) extract $(MOCK_PDF) --mock
	@echo "=================================="
	$(RESUME_CLI) score $(MOCK_PDF) --jd $(JD) --mock

parse:
	$(RESUME_CLI) parse $(PDF)

extract:
	$(RESUME_CLI) extract $(PDF)

score:
	$(RESUME_CLI) score $(PDF) --jd $(JD)
