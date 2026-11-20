class ExperimentTrackerError(Exception):
    """所有exp_traker异常基类"""

class ValidationError(ExperimentTrackerError):
    """数据校验失败"""

class StorageError(ExperimentTrackerError):
    """存储层失败"""

class ExperimentNotFoundError(ExperimentTrackerError):
    """找不到实验id"""