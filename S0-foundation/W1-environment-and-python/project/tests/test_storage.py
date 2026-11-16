"""
JsonExperimentStore 的单元测试。

运行方式（在 project/ 目录下）：

    python3 -m unittest tests.test_storage -v

测试重点：
- 初始化时自动创建父目录和空文件
- add/list/find/delete 正常路径
- 找不到 ID 时抛 ExperimentNotFoundError
- 重复 ID、损坏 JSON、顶层不是列表时抛 StorageError
- 新建 store 能读到之前写入的数据（持久化）
"""

import json
import tempfile
import unittest
from pathlib import Path

from exp_tracker.errors import ExperimentNotFoundError, StorageError
from exp_tracker.models import Experiment
from exp_tracker.storage import JsonExperimentStore


def make_experiment(experiment_id="store001"):
    """构造一条测试用实验。"""
    return Experiment(
        name="demo-exp",
        model="Qwen2.5-7B",
        learning_rate=1e-4,
        batch_size=8,
        accuracy=0.923,
        loss=0.214,
        experiment_id=experiment_id,
    )


class TestJsonExperimentStore(unittest.TestCase):
    """每个测试用独立的临时目录，互不污染。"""

    def setUp(self):
        # TemporaryDirectory 会在 tearDown 时递归删除目录
        self.temp_dir = tempfile.TemporaryDirectory()

        # 故意多一层 data/，测试“父目录不存在时自动创建”
        self.data_file = Path(self.temp_dir.name) / "data" / "experiments.json"

        # 创建 store 时会自动建目录和空文件
        self.store = JsonExperimentStore(self.data_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initializes_empty_file(self):
        """初始化后文件存在，内容为空列表。"""
        self.assertTrue(self.data_file.exists())
        self.assertEqual(self.store.list_all(), [])

    def test_add_and_list(self):
        """添加后能列出，且对象相等。"""
        exp = make_experiment()
        self.store.add(exp)

        experiments = self.store.list_all()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments[0], exp)

    def test_find_by_id(self):
        """按 ID 能查到。"""
        exp = make_experiment()
        self.store.add(exp)
        self.assertEqual(self.store.find_by_id("store001"), exp)

    def test_find_missing_raises(self):
        """找不到 ID 时抛 ExperimentNotFoundError。"""
        with self.assertRaises(ExperimentNotFoundError):
            self.store.find_by_id("missing")

    def test_delete(self):
        """删除返回被删对象，列表变空。"""
        exp = make_experiment()
        self.store.add(exp)

        deleted = self.store.delete("store001")
        self.assertEqual(deleted, exp)
        self.assertEqual(self.store.list_all(), [])

    def test_delete_missing_raises(self):
        """删除不存在的 ID 时抛 ExperimentNotFoundError。"""
        with self.assertRaises(ExperimentNotFoundError):
            self.store.delete("missing")

    def test_duplicate_id_raises(self):
        """同一个 ID 添加两次，第二次抛 StorageError。"""
        self.store.add(make_experiment())

        with self.assertRaises(StorageError):
            self.store.add(make_experiment())

    def test_persistence_across_instances(self):
        """新建 store 指向同一文件，能读到之前写入的数据。"""
        self.store.add(make_experiment())

        another_store = JsonExperimentStore(self.data_file)
        self.assertEqual(len(another_store.list_all()), 1)

    def test_corrupted_json_raises_storage_error(self):
        """文件不是合法 JSON 时，抛 StorageError 而不是 JSONDecodeError。"""
        self.data_file.write_text("{not valid json", encoding="utf-8")

        with self.assertRaises(StorageError):
            self.store.list_all()

    def test_top_level_must_be_list(self):
        """顶层是对象而不是列表时，抛 StorageError。"""
        self.data_file.write_text(json.dumps({"name": "x"}), encoding="utf-8")

        with self.assertRaises(StorageError):
            self.store.list_all()


if __name__ == "__main__":
    unittest.main()
