"""resume-cli 统一异常定义。

为什么单独定义一套异常:
- CLI 面向的是普通用户,任何预期内的错误都不能把 Python traceback 直接抛给用户(需求 §34);
- 因此所有"可预期的业务错误"统一继承 ResumeCliError,
  由命令入口集中捕获,并输出一行友好的 "Error: ..." + 非 0 退出码;
- 按错误类型细分(文件 / PDF / AI / 数据),便于后续阶段分类处理。
"""


class ResumeCliError(Exception):
    """所有可预期业务错误的基类,错误信息会以 "Error: ..." 形式展示给用户。"""


class PDFNotFoundError(ResumeCliError):
    """PDF 文件不存在。"""


class PathIsNotFileError(ResumeCliError):
    """输入路径是目录而不是普通文件。"""


class NotPDFError(ResumeCliError):
    """文件扩展名不是 .pdf。"""


class PDFReadError(ResumeCliError):
    """PDF 无法被解析器打开(损坏、加密或伪造的 PDF)。"""
