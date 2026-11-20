"""
Experiment 模型的单元测试。

运行方式（在 project/ 目录下）：

    python3 -m unittest tests.test_models -v

测试重点：
- 合法数据能创建对象
- 非法数据抛 ValidationError
- to_dict / from_dict 往返一致
- __eq__ 按 ID 比较
"""

import unittest

from ..exp_tracker.errors import ValidationError
from ..exp_tracker.models import Experiment


def make_experiment(**overrides):
    """构造一条测试用的合法实验；overrides 用来替换个别字段。

    这样每个测试只写“这次要改哪个字段”，不用重复整份数据。
    """

    data = {
        "name": "demo-exp",
        "model": "Qwen2.5-7B",
        "learning_rate": 1e-4,
        "batch_size": 8,
        "accuracy": 0.923,
        "loss": 0.214,
        "notes": "unit test",
        "experiment_id": "test0001",
        "created_at": "2026-11-16T09:00:00",
    }
    data.update(overrides)  # 用传入的字段覆盖默认值
    return Experiment(**data)


class TestExperiment(unittest.TestCase):
    """Experiment 的行为测试。"""

    def test_valid_experiment(self):
        """合法数据：字段正确、is_successful 为 True。"""
        exp = make_experiment()

        self.assertEqual(exp.experiment_id, "test0001")
        self.assertEqual(exp.name, "demo-exp")
        self.assertAlmostEqual(exp.accuracy, 0.923)
        self.assertTrue(exp.is_successful)

    def test_invalid_accuracy(self):
        """accuracy 超出 0~1：必须抛 ValidationError。"""
        with self.assertRaises(ValidationError):
            make_experiment(accuracy=1.5)

    def test_invalid_learning_rate(self):
        """学习率为 0：必须抛 ValidationError。"""
        with self.assertRaises(ValidationError):
            make_experiment(learning_rate=0)

    def test_empty_name(self):
        """名字只有空白：strip 后为空，必须抛 ValidationError。"""
        with self.assertRaises(ValidationError):
            make_experiment(name="   ")

    def test_to_from_dict_roundtrip(self):
        """to_dict 后再 from_dict，字段应完全一致。"""
        exp = make_experiment()
        restored = Experiment.from_dict(exp.to_dict())

        self.assertEqual(exp, restored)
        self.assertEqual(exp.to_dict(), restored.to_dict())

    def test_from_dict_missing_key(self):
        """缺少必填字段：必须抛 ValidationError，并提示缺了什么。"""
        with self.assertRaises(ValidationError):
            Experiment.from_dict({"name": "x"})

    def test_equality_by_id(self):
        """相等性按 ID 判断：ID 相同即相等，即使其他字段不同。"""
        a = make_experiment()
        b = make_experiment(name="other-name")
        c = make_experiment(experiment_id="test0002")

        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_repr_contains_id(self):
        """repr 应包含 ID，方便调试时辨认。"""
        exp = make_experiment()
        self.assertIn("test0001", repr(exp))


if __name__ == "__main__":
    # 直接运行本文件时执行测试；被 unittest discover 时不会重复执行
    unittest.main()
