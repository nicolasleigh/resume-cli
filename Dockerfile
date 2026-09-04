# resume-cli 运行镜像。
# 构建:docker build -t resume-cli .
# 运行示例:
#   docker run --rm resume-cli --help
#   docker run --rm resume-cli parse /app/examples/resume.pdf
#   docker run --rm resume-cli extract /app/examples/resume.pdf --mock
FROM python:3.12-slim

WORKDIR /app

# 先只复制构建所需文件,利用 Docker 层缓存:依赖层不变时不会重复安装。
COPY pyproject.toml README.md ./
COPY src ./src

# 安装运行时依赖与包本身(不需要 dev/pytest)。
RUN pip install --no-cache-dir .

# 示例 PDF/JD 放入镜像,便于直接演示 parse/extract/score。
COPY examples ./examples

# 容器入口即 resume-cli 命令。
ENTRYPOINT ["resume-cli"]
