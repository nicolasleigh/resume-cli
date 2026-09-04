"""resume-cli 日志配置(Phase 16)。

为什么日志输出到 stderr 而不是 stdout:
- 命令的结果(简历文本 / JSON)走 stdout,方便重定向与管道;
- 日志走 stderr,不会污染结果输出(§31 示例里日志与结果并存于终端)。

隐私与安全约定(§31):
- 绝不把 OPENAI_API_KEY 写进日志;
- 默认只记录文件读取、字符数、调用阶段等信息,不打印完整候选人简历内容。
"""

import logging
import sys

# 统一的 INFO 日志:示例输出形如 "INFO Reading PDF"。
_FORMAT = "%(levelname)s %(message)s"


def setup_logger(name: str = "resume-cli") -> logging.Logger:
    """创建并返回一个输出到 stderr 的 logger(幂等,重复调用不重复加 handler)。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        # 防止日志再冒泡到 root logger 造成重复输出。
        logger.propagate = False
    return logger


# 模块级单例:业务代码直接 import 后使用。
logger = setup_logger()
