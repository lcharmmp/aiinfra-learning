"""
Day 2 示例：__repr__ / __str__ / __eq__、继承、组合、property、
@classmethod、@staticmethod。

运行方式（在 W1 目录下）：

    python3 examples/day2_oop_advanced.py
"""


class ModelConfig:
    """模型配置：作为组合示例，被 EvalExperiment 持有。"""

    def __init__(self, model_name, precision="fp16"):
        self.model_name = model_name   # 模型名
        self.precision = precision     # 精度，例如 fp16 / awq

    def describe(self):
        """返回一行描述，供持有它的对象调用。"""
        return f"{self.model_name} ({self.precision})"

    def __repr__(self):
        return (
            f"ModelConfig(model_name={self.model_name!r}, "
            f"precision={self.precision!r})"
        )


class Experiment:
    """所有实验的基类。"""

    def __init__(self, name, model, accuracy):
        self.name = name
        self.model = model
        # 这里会触发 accuracy 的 setter，做范围校验
        self.accuracy = accuracy

    # ------------------------------------------------------------------
    # @property：把方法伪装成属性，访问时不用加括号
    # ------------------------------------------------------------------
    @property
    def accuracy(self):
        """读取 accuracy。"""
        return self._accuracy

    @accuracy.setter
    def accuracy(self, value):
        """设置 accuracy 时做类型和范围校验。"""
        if not isinstance(value, (int, float)):
            raise ValueError(f"accuracy 必须是数字，收到 {type(value).__name__}")
        if not 0 <= value <= 1:
            raise ValueError(f"accuracy 必须在 0 到 1 之间，收到 {value}")
        # 真正的存储放在 _accuracy，避免和 property 同名导致递归
        self._accuracy = float(value)

    @property
    def is_successful(self):
        """只读计算属性：准确率 >= 0.9 视为成功。"""
        return self._accuracy >= 0.9

    # ------------------------------------------------------------------
    # 普通实例方法：子类可以覆盖
    # ------------------------------------------------------------------
    def summary(self):
        return (
            f"{self.name} | {self.model} | "
            f"acc={self.accuracy:.3f}"
        )

    # ------------------------------------------------------------------
    # 工厂方法：从字典创建对象
    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data):
        """cls 是类本身；子类调用时会得到子类。"""
        return cls(
            name=data["name"],
            model=data["model"],
            accuracy=data["accuracy"],
        )

    # ------------------------------------------------------------------
    # 静态方法：只是逻辑上属于这个类，不需要 self/cls
    # ------------------------------------------------------------------
    @staticmethod
    def format_accuracy(value):
        """把 0.923 格式化成 "92.3%"。"""
        return f"{value:.1%}"

    # ------------------------------------------------------------------
    # 魔术方法
    # ------------------------------------------------------------------
    def __repr__(self):
        """给开发者看的精确表示。"""
        return (
            f"Experiment(name={self.name!r}, "
            f"model={self.model!r}, "
            f"accuracy={self.accuracy!r})"
        )

    def __str__(self):
        """给用户看的可读表示；print(exp) 优先用它。"""
        return f"{self.name}（准确率 {self.accuracy:.1%}）"

    def __eq__(self, other):
        """按 name + model + accuracy 判断是否相等。"""
        if not isinstance(other, Experiment):
            return NotImplemented
        return (
            self.name == other.name
            and self.model == other.model
            and self.accuracy == other.accuracy
        )


class TrainingExperiment(Experiment):
    """训练实验：继承 Experiment，增加学习率和 batch size。"""

    def __init__(self, name, model, accuracy, learning_rate, batch_size):
        # 先调用父类构造方法，初始化共同字段
        super().__init__(name, model, accuracy)
        # 再初始化子类特有字段
        self.learning_rate = learning_rate
        self.batch_size = batch_size

    def summary(self):
        """覆盖父类方法：先复用父类摘要，再追加字段。"""
        base = super().summary()
        return (
            f"{base} | lr={self.learning_rate:g} | "
            f"bs={self.batch_size}"
        )


class EvalExperiment:
    """评测实验：用组合持有一个 ModelConfig，而不是继承它。"""

    def __init__(self, name, config, accuracy):
        self.name = name
        self.config = config      # has-a：EvalExperiment 有一个 ModelConfig
        self.accuracy = accuracy

    def summary(self):
        # 通过持有的对象调用它的方法
        return (
            f"{self.name} | {self.config.describe()} | "
            f"acc={self.accuracy:.3f}"
        )


def main():
    """演示所有概念。"""

    print("=" * 60)
    print("1. 基础类 + __repr__ / __str__ / __eq__ / property")
    print("=" * 60)

    base = Experiment("base-eval", "Qwen2.5-7B", 0.923)
    print("str(base):", str(base))
    print("repr(base):", repr(base))
    print("is_successful:", base.is_successful)

    # __eq__：字段相同则相等
    same = Experiment("base-eval", "Qwen2.5-7B", 0.923)
    different = Experiment("base-eval", "Qwen2.5-7B", 0.80)
    print("base == same:", base == same)
    print("base == different:", base == different)

    # property setter 校验
    try:
        base.accuracy = 1.5
    except ValueError as exc:
        print("设置非法 accuracy 被拒绝:", exc)

    print()

    print("=" * 60)
    print("2. 继承 + 多态")
    print("=" * 60)

    train = TrainingExperiment(
        name="qwen-lr1e-4",
        model="Qwen2.5-7B",
        accuracy=0.935,
        learning_rate=1e-4,
        batch_size=8,
    )
    print("train.summary():", train.summary())
    print("train 是 Experiment 吗:", isinstance(train, Experiment))

    # 多态：统一调用 summary()
    experiments = [base, train]
    for exp in experiments:
        print("  ", exp.summary())

    print()

    print("=" * 60)
    print("3. 组合")
    print("=" * 60)

    config = ModelConfig("Qwen2.5-7B-Instruct", "awq")
    eval_exp = EvalExperiment("awq-eval", config, 0.917)
    print("eval_exp.summary():", eval_exp.summary())
    print("eval_exp.config:", eval_exp.config)

    print()

    print("=" * 60)
    print("4. @classmethod / @staticmethod")
    print("=" * 60)

    from_dict_exp = Experiment.from_dict(
        {"name": "from-dict", "model": "Qwen2.5-7B", "accuracy": 0.88}
    )
    print("from_dict_exp:", repr(from_dict_exp))
    print("format_accuracy:", Experiment.format_accuracy(0.923))

    print()

    print("=" * 60)
    print("5. 容器里的 __repr__")
    print("=" * 60)

    print([base, train, from_dict_exp])


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------
# 练习
# ----------------------------------------------------------------------
# 1. 给 Experiment 加 @property method is_failed：
#      accuracy < 0.6 时返回 True。
#
# 2. 写 BenchmarkExperiment(Experiment)：
#      额外字段：concurrency、ttft_ms、tpot_ms
#      summary() 在父类基础上追加这三个字段。
#
# 3. 写一个 EvalExperiment.from_dict 类方法：
#      输入包含 name/model/precision/accuracy 的字典，
#      内部先创建 ModelConfig，再创建 EvalExperiment。
#
# 4. 解释：为什么 EvalExperiment 用组合而不是继承 ModelConfig？
