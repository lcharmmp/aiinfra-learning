"""
exp_tracker.errors
==================

自定义异常模块。

为什么需要自定义异常？
---------------------
Python 内置的 ValueError / FileNotFoundError 表达的是“语言层面”的错误。
业务错误（实验不存在、数据校验失败、JSON 损坏）如果也用内置异常，
调用方很难区分“真的是输入格式错了”还是“业务规则不允许”。

自定义异常带来三个好处：

1. 名字本身就是文档：看到 ExperimentNotFoundError 就知道发生了什么。
2. 可以精确捕获：CLI 只捕获 ExperimentTrackerError，不会误吞其他 bug。
3. 可以建层级：所有业务异常继承同一个基类，调用方可以先统一兜底，
   再按需捕获更具体的子类。

异常层级
--------
ExperimentTrackerError
├── ValidationError          数据不合法（空名字、accuracy 越界等）
├── StorageError             读/写 JSON 失败、数据损坏、ID 重复
└── ExperimentNotFoundError  按 ID 找不到实验

W2 会继续补充：
- 异常链 raise ... from ... 的最佳实践
- 日志里如何记录异常
- 哪些异常应该重试，哪些不应该
"""


class ExperimentTrackerError(Exception):
    """所有 exp_tracker 业务异常的基类。

    继承 Exception 而不是 BaseException，原因：
    - BaseException 还包括 KeyboardInterrupt、SystemExit 等“系统级退出”信号，
      业务代码不应该把它们当成普通错误吞掉。
    - Exception 才是“程序可以处理”的错误。
    """


class ValidationError(ExperimentTrackerError):
    """数据校验失败。

    触发场景举例：
    - 实验名为空
    - accuracy 不在 0~1 之间
    - learning_rate <= 0
    - 从 JSON 反序列化时缺少必填字段
    """


class StorageError(ExperimentTrackerError):
    """存储层失败。

    触发场景举例：
    - JSON 文件损坏，无法解析
    - 文件没有读/写权限
    - 同一个 experiment_id 被重复添加
    - JSON 顶层不是列表，或某条记录不是对象
    """


class ExperimentNotFoundError(ExperimentTrackerError):
    """按 ID 查找/删除实验时，记录不存在。"""
