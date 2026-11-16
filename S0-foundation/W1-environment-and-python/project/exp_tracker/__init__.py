"""
exp_tracker
===========

实验记录器包。

__init__.py 的作用：
1. 标记这个目录是一个常规 Python 包。
2. 把常用名字提升到包级别，外部可以写：

       from exp_tracker import Experiment, ExperimentService

   而不必记住每个类在哪个子模块。
3. 用 __all__ 控制 `from exp_tracker import *` 时导出哪些名字。

注意：
- 这里只做“重新导出”，不写业务逻辑。
- 导入顺序要小心：errors 是叶子模块，先导入它不会引发循环依赖。
"""

# 异常层级：先导入基类和具体异常
from .errors import (
    ExperimentNotFoundError,
    ExperimentTrackerError,
    StorageError,
    ValidationError,
)

# 数据模型
from .models import Experiment

# 存储层
from .storage import JsonExperimentStore

# 业务层
from .service import ExperimentService

# 明确声明包的公开 API
__all__ = [
    "ExperimentTrackerError",
    "ValidationError",
    "StorageError",
    "ExperimentNotFoundError",
    "Experiment",
    "JsonExperimentStore",
    "ExperimentService",
]
