# resume-cli 常用命令入口(锦上添花)。
# 用法示例:
#   make install        # 创建 .venv 并安装(含 dev 依赖)
#   make test           # 运行 pytest
#   make demo           # 依次演示 parse / extract --mock / score --mock

PYTHON     ?= .venv/bin/python
RESUME_CLI ?= .venv/bin/resume-cli
PDF        ?= examples/resume.pdf
JD         ?= examples/jd.txt

.PHONY: help install generate-examples test demo parse extract score

help:
	@echo "可用目标:"
	@echo "  make install            创建 .venv 并安装依赖(含 dev)"
	@echo "  make generate-examples  生成 examples/resume.pdf 与 blank.pdf"
	@echo "  make test               运行 pytest"
	@echo "  make demo               依次演示 parse / extract --mock / score --mock"
	@echo "  make parse              运行 resume-cli parse examples/resume.pdf"
	@echo "  make extract            运行 resume-cli extract examples/resume.pdf --mock"
	@echo "  make score              运行 resume-cli score examples/resume.pdf --jd examples/jd.txt --mock"

install:
	python3.12 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

generate-examples:
	$(PYTHON) examples/generate_sample_pdfs.py

test:
	$(PYTHON) -m pytest -q

demo: generate-examples
	$(RESUME_CLI) parse $(PDF)
	@echo "=================================="
	$(RESUME_CLI) extract $(PDF) --mock
	@echo "=================================="
	$(RESUME_CLI) score $(PDF) --jd $(JD) --mock

parse:
	$(RESUME_CLI) parse $(PDF)

extract:
	$(RESUME_CLI) extract $(PDF) --mock

score:
	$(RESUME_CLI) score $(PDF) --jd $(JD) --mock
