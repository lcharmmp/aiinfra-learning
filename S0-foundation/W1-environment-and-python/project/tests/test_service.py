"""
ExperimentService 的单元测试。

运行方式（在 project/ 目录下）：

    python3 -m unittest tests.test_service -v

测试重点：
- 空数据时 summary 返回稳定结构
- 添加/列表/查找/删除
- 汇总统计（最高准确率、平均 loss、模型去重排序）
- 校验失败时不会写入存储
"""

import tempfile
import unittest
from pathlib import Path

from exp_tracker.errors import ExperimentNotFoundError, ValidationError
from exp_tracker.service import ExperimentService
from exp_tracker.storage import JsonExperimentStore


class TestExperimentService(unittest.TestCase):
    """每个测试用独立的临时文件。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_file = Path(self.temp_dir.name) / "experiments.json"
        self.store = JsonExperimentStore(data_file)
        self.service = ExperimentService(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _add(self, name="exp-a", model="Qwen2.5-7B", accuracy=0.9, loss=0.2):
        """测试辅助：添加一条实验，减少重复参数。"""
        return self.service.add_experiment(
            name=name,
            model=model,
            learning_rate=1e-4,
            batch_size=8,
            accuracy=accuracy,
            loss=loss,
            notes="",
        )

    def test_summary_empty(self):
        """空数据：count=0，其他字段为 None/[]。"""
        summary = self.service.summary()

        self.assertEqual(summary["count"], 0)
        self.assertIsNone(summary["best_accuracy"])
        self.assertIsNone(summary["average_loss"])
        self.assertEqual(summary["models"], [])

    def test_add_and_list(self):
        """添加后能列出。"""
        exp = self._add()

        experiments = self.service.list_experiments()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments[0], exp)

    def test_summary(self):
        """两条数据：最高准确率、平均 loss、模型列表都正确。"""
        self._add(name="a", accuracy=0.8, loss=0.3)
        self._add(name="b", accuracy=0.95, loss=0.1)

        summary = self.service.summary()

        self.assertEqual(summary["count"], 2)
        self.assertAlmostEqual(summary["best_accuracy"], 0.95)
        self.assertAlmostEqual(summary["average_loss"], 0.2)
        self.assertEqual(summary["models"], ["Qwen2.5-7B"])

    def test_find_and_delete(self):
        """查找、删除、删除后再查应报错。"""
        exp = self._add()

        found = self.service.find_experiment(exp.experiment_id)
        self.assertEqual(found, exp)

        self.service.delete_experiment(exp.experiment_id)
        self.assertEqual(self.service.list_experiments(), [])

        with self.assertRaises(ExperimentNotFoundError):
            self.service.find_experiment(exp.experiment_id)

    def test_validation_error_does_not_store(self):
        """校验失败时抛异常，且存储里不应留下任何记录。"""
        with self.assertRaises(ValidationError):
            self.service.add_experiment(
                name="bad",
                model="m",
                learning_rate=1e-4,
                batch_size=8,
                accuracy=2.0,  # 非法
                loss=0.1,
            )

        self.assertEqual(self.service.list_experiments(), [])


if __name__ == "__main__":
    unittest.main()
