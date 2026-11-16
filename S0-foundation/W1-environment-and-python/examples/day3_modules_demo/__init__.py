"""
day3_modules_demo 包。

这个文件让 Python 把目录识别为“常规包”。

同时，它把常用函数提升到包级别，外部可以：

    from day3_modules_demo import add, multiply

而不必写：

    from day3_modules_demo.math_utils import add
"""

# 从子模块重新导出函数
from .math_utils import add, multiply
from .text_utils import count_words

# __all__ 控制 `from day3_modules_demo import *` 时导出哪些名字
__all__ = ["add", "multiply", "count_words"]
