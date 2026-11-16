"""
exp_tracker.storage
===================

存储层：负责把 Experiment 读写到 JSON 文件。

为什么单独一层？
----------------
- 业务层（service）不应该知道“数据存在 JSON 还是 SQLite”。
- 以后要换数据库，只需要改这一层，service 不用动。
- 测试时可以用临时目录创建独立的 store，互不干扰。

W1 选 JSON 的原因：
- 标准库自带，2C2G 服务器不用装任何依赖。
- 人类可读，方便你直接打开文件检查。
- 足以支撑几十~几百条实验记录。

W2 会讨论：
- 原子写入的更多细节
- 文件锁与并发
- 为什么生产环境通常不用 JSON 文件做存储
"""

import json
from pathlib import Path

from .errors import ExperimentNotFoundError, StorageError, ValidationError
from .models import Experiment


class JsonExperimentStore:
    """基于 JSON 文件的实验存储。

    数据文件格式：一个 JSON 数组，每个元素是一条实验记录：

        [
          {
            "experiment_id": "a1b2c3d4",
            "name": "...",
            ...
          }
        ]

    这个类只负责持久化，不做业务汇总。
    """

    def __init__(self, data_file):
        """初始化存储。

        参数
        ----
        data_file : str | Path
            JSON 文件路径。父目录不存在会自动创建。
        """

        # Path 对象比字符串好用：拼接、判断存在、创建目录、原子替换都更方便
        self.data_file = Path(data_file)

        # 确保父目录存在，并在文件不存在时写入一个空列表
        self._ensure_storage()

    # ------------------------------------------------------------------
    # 内部方法：文件初始化 / 读取 / 写入
    # ------------------------------------------------------------------

    def _ensure_storage(self):
        """确保数据文件存在；不存在就创建空数组。"""

        # parents=True：父目录不存在时逐级创建
        # exist_ok=True：目录已存在时不报错
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            # 新文件从空列表开始，保证后续 json.load 永远能拿到 list
            self._write_all([])

    def _read_all(self):
        """读取并校验所有记录，返回 Experiment 列表。

        任何底层错误都会包装成 StorageError，并保留原始异常链。
        这样 service/cli 只需要捕获业务异常，不需要知道 json/pathlib 的细节。
        """

        # 读取整个文件；文件可能被删除/没有权限
        try:
            text = self.data_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"读取数据文件失败: {self.data_file}") from exc

        # 空文件（或只有空白）当成空列表，避免 JSONDecodeError
        if not text.strip():
            return []

        # 解析 JSON；损坏的文件要明确报错，而不是悄悄返回空列表
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise StorageError(f"数据文件不是合法 JSON: {self.data_file}") from exc

        # 顶层必须是数组，否则结构不对
        if not isinstance(raw, list):
            raise StorageError("数据文件的顶层必须是列表")

        experiments = []
        for index, item in enumerate(raw):
            # 每条记录必须是对象，才能按字段读取
            if not isinstance(item, dict):
                raise StorageError(f"第 {index} 条记录不是 JSON 对象")

            try:
                # Experiment.from_dict 会做字段检查和业务校验
                experiments.append(Experiment.from_dict(item))
            except ValidationError as exc:
                # 把“第几条记录坏了”带上，方便定位
                raise StorageError(f"第 {index} 条记录校验失败: {exc}") from exc

        return experiments

    def _write_all(self, experiments):
        """把所有记录写回 JSON 文件。

        采用“先写临时文件，再原子替换”的方式：
        1. 写 experiments.json.tmp
        2. 用 replace 把 tmp 改名成正式文件

        这样即使写入过程中进程崩溃，正式文件也不会出现“写了一半”的损坏状态。
        在同一个文件系统内，Path.replace 是原子操作。
        """

        # 先把对象转成字典，再统一序列化
        payload = [experiment.to_dict() for experiment in experiments]

        # 临时文件与正式文件同目录，保证 replace 是同一文件系统内的原子操作
        tmp_file = self.data_file.with_name(self.data_file.name + ".tmp")

        try:
            # ensure_ascii=False：让中文备注直接可读，而不是 \uXXXX
            # indent=2：方便人直接打开文件检查
            tmp_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # 原子替换：要么看到旧文件，要么看到完整的新文件
            tmp_file.replace(self.data_file)
        except OSError as exc:
            raise StorageError(f"写入数据文件失败: {self.data_file}") from exc

    # ------------------------------------------------------------------
    # 对外接口
    # ------------------------------------------------------------------

    def add(self, experiment):
        """添加一条实验记录，返回同一个对象。"""

        # 这是程序员调用错误，不是用户输入错误，所以用 TypeError 而不是业务异常
        if not isinstance(experiment, Experiment):
            raise TypeError("add() 只接受 Experiment 对象")

        experiments = self._read_all()

        # ID 必须唯一；重复说明调用方逻辑有问题，直接拒绝
        if any(item.experiment_id == experiment.experiment_id for item in experiments):
            raise StorageError(f"实验 ID 已存在: {experiment.experiment_id}")

        experiments.append(experiment)
        self._write_all(experiments)
        return experiment

    def list_all(self):
        """返回所有实验记录（新列表，调用方修改不会影响文件）。"""
        return self._read_all()

    def find_by_id(self, experiment_id):
        """按 ID 查找；找不到抛 ExperimentNotFoundError。"""
        for experiment in self._read_all():
            if experiment.experiment_id == experiment_id:
                return experiment
        raise ExperimentNotFoundError(f"找不到实验: {experiment_id}")

    def delete(self, experiment_id):
        """按 ID 删除并返回被删除的记录；找不到抛异常。"""
        experiments = self._read_all()

        for index, experiment in enumerate(experiments):
            if experiment.experiment_id == experiment_id:
                deleted = experiments.pop(index)
                self._write_all(experiments)
                return deleted

        raise ExperimentNotFoundError(f"找不到实验: {experiment_id}")

    def count(self):
        """返回记录数量。"""
        return len(self._read_all())
