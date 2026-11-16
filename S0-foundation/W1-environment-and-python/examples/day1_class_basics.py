"""
Day 1 示例：类、对象、__init__、self、实例属性、类属性、方法。

运行方式（在 W1 目录下）：

    python3 examples/day1_class_basics.py

读法：
1. 先看 ModelConfig 的定义，注意 __init__ 和 self。
2. 再看 main() 里怎么创建对象、访问属性、调用方法。
3. 最后做文件末尾注释里的练习。
"""


class ModelConfig:
    """模型配置：演示类、实例、属性、方法。"""

    # 类属性：所有实例共享的一份数据。
    # 这里表示默认精度；某个实例可以单独改自己的 precision。
    default_precision = "fp16"

    def __init__(self, name, hidden_size, num_layers):
        """构造方法：创建对象时自动调用。

        参数
        ----
        name : str
            模型名。
        hidden_size : int
            隐藏层维度。
        num_layers : int
            层数。
        """

        # 实例属性：每个对象各自一份。
        # self.name 表示“挂到当前对象上的 name”。
        self.name = name
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # 从类属性取默认值，挂到实例上。
        # 这样以后改 config.precision 只影响这个实例。
        self.precision = self.default_precision

    def describe(self):
        """返回一段人类可读的描述。"""

        # f-string 里可以直接访问 self 的属性
        return (
            f"ModelConfig(name={self.name}, "
            f"hidden_size={self.hidden_size}, "
            f"num_layers={self.num_layers}, "
            f"precision={self.precision})"
        )

    def is_tiny(self):
        """判断是不是“很小的模型”。

        用途：在 2C2G 服务器上做逻辑验证时，只跑小配置。
        """

        return self.hidden_size <= 256 and self.num_layers <= 6

    def __repr__(self):
        """给开发者看的精确表示；print([config]) 时会用到。"""

        return (
            f"ModelConfig(name={self.name!r}, "
            f"hidden_size={self.hidden_size!r}, "
            f"num_layers={self.num_layers!r})"
        )


class DatasetConfig:
    """数据集配置：练习类、属性、方法（Day 1 练习参考答案）。"""

    def __init__(self, name, num_samples, seq_len):
        self.name = name                  # 数据集名
        self.num_samples = num_samples    # 样本数
        self.seq_len = seq_len            # 每条样本的 token 长度

    def total_tokens(self):
        """总 token 数 = 样本数 × 每条长度。"""

        return self.num_samples * self.seq_len

    def describe(self):
        return (
            f"DatasetConfig(name={self.name}, "
            f"num_samples={self.num_samples}, "
            f"seq_len={self.seq_len}, "
            f"total_tokens={self.total_tokens()})"
        )


def main():
    """演示区：创建对象、访问属性、调用方法。"""

    # 创建 ModelConfig 实例；参数会传给 __init__
    tiny = ModelConfig("tiny-transformer", hidden_size=128, num_layers=4)

    # 访问实例属性
    print("模型名:", tiny.name)
    print("隐藏维度:", tiny.hidden_size)

    # 访问类属性（通过实例也能访问到）
    print("默认精度:", tiny.default_precision)

    # 调用实例方法；注意不需要手动传 self
    print(tiny.describe())
    print("是小模型吗:", tiny.is_tiny())

    # 修改实例属性；不会影响类属性
    tiny.precision = "int8"
    print("修改后的精度:", tiny.precision)
    print("类属性仍是:", ModelConfig.default_precision)

    # 再创建一个对象，验证实例属性互不影响
    small = ModelConfig("small-transformer", hidden_size=512, num_layers=8)
    print(small.describe())
    print("是小模型吗:", small.is_tiny())

    # __repr__ 的效果
    print("repr:", repr(tiny))
    print("放进列表:", [tiny, small])

    # DatasetConfig 演示
    dataset = DatasetConfig("toy-cn", num_samples=1000, seq_len=512)
    print(dataset.describe())


# 只有直接运行本文件时才执行 main()；被 import 时不执行
if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------
# 练习（先自己写，再运行验证）
# ----------------------------------------------------------------------
# 1. 给 ModelConfig 增加一个方法 estimate_params()：
#      参数量 ≈ 12 * num_layers * hidden_size ** 2
#    返回整数，并在 main() 里打印 tiny 和 small 的估计参数量。
#
# 2. 给 DatasetConfig 增加一个方法 is_long_context()：
#      seq_len >= 4096 时返回 True。
#
# 3. 创建一个 ModelConfig，把 precision 设为 "awq"，
#    并解释：这个修改会不会影响其他 ModelConfig 对象？为什么？
