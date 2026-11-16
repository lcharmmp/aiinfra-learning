# Python 类与对象一页纸

---

## 最小类

```python
class ModelConfig:
    """类文档字符串：说明这个类是什么。"""

    default_precision = "fp16"          # 类属性：所有实例共享

    def __init__(self, name, hidden_size):
        self.name = name                # 实例属性：每个对象独立
        self.hidden_size = hidden_size
        self.precision = self.default_precision

    def describe(self):                 # 实例方法：第一个参数是 self
        return f"{self.name}: {self.hidden_size}, {self.precision}"


config = ModelConfig("tiny", 128)       # 创建对象，自动调用 __init__
print(config.name)                      # 访问属性
print(config.describe())                # 调用方法，不传 self
```

要点：

- `self` 是当前对象，Python 自动传入。
- 定义方法时第一个参数写 `self`；调用时不传。
- `self.x = x` 才是实例属性；只写 `x = x` 是局部变量。

---

## 实例属性 vs 类属性

```python
class Demo:
    category = "experiment"     # 类属性：共享

    def __init__(self, name):
        self.name = name        # 实例属性：独立
        self.items = []         # 可变对象一定放实例里


a = Demo("a")
b = Demo("b")

a.category = "custom"           # 在 a 上创建实例属性，遮蔽类属性
print(a.category, b.category, Demo.category)  # custom experiment experiment
```

**坑：** 可变类属性（`items = []`）会被所有实例共享；可变容器放 `__init__`。

---

## 常用魔术方法

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    def __repr__(self):                     # 开发者看；调试/容器
        return f"Experiment(name={self.name!r}, accuracy={self.accuracy!r})"

    def __str__(self):                      # 用户看；print 优先用它
        return f"{self.name}（{self.accuracy:.1%}）"

    def __eq__(self, other):                # 定义 ==
        if not isinstance(other, Experiment):
            return NotImplemented
        return self.name == other.name and self.accuracy == other.accuracy
```

记忆：

```text
repr()  -> 开发者 / 调试 / 列表打印
str()   -> 用户 / print
没有 __str__ 时，print 退回 __repr__
```

**坑：** `is` 比较身份，`==` 比较值；定义 `__eq__` 后对象默认不可哈希。

---

## 继承（is-a）

```python
class Experiment:
    def __init__(self, name, model, accuracy):
        self.name = name
        self.model = model
        self.accuracy = accuracy

    def summary(self):
        return f"{self.name} | {self.model} | acc={self.accuracy:.3f}"


class TrainingExperiment(Experiment):
    def __init__(self, name, model, accuracy, learning_rate, batch_size):
        super().__init__(name, model, accuracy)   # 先初始化父类字段
        self.learning_rate = learning_rate
        self.batch_size = batch_size

    def summary(self):                            # 覆盖父类方法
        return f"{super().summary()} | lr={self.learning_rate:g} | bs={self.batch_size}"
```

要点：

- `super().__init__(...)` 必须调用，否则父类字段不存在。
- 子类对象也是父类类型：`isinstance(train, Experiment)` 为 True。
- 多态：统一调用 `summary()`，不关心具体子类。

---

## 组合（has-a）

```python
class ModelConfig:
    def __init__(self, model_name, precision="fp16"):
        self.model_name = model_name
        self.precision = precision

    def describe(self):
        return f"{self.model_name} ({self.precision})"


class EvalExperiment:
    def __init__(self, name, config, accuracy):
        self.name = name
        self.config = config      # has-a：持有一个 ModelConfig
        self.accuracy = accuracy

    def summary(self):
        return f"{self.name} | {self.config.describe()} | acc={self.accuracy:.3f}"
```

选择：

- **is-a**：训练实验是一种实验 → 继承。
- **has-a**：实验有一个模型配置 → 组合。
- 只是共享几个字段，没有“是一种”关系 → 优先组合。

---

## @property

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy        # 触发 setter

    @property
    def accuracy(self):                 # 读取
        return self._accuracy

    @accuracy.setter
    def accuracy(self, value):          # 写入时校验
        if not 0 <= value <= 1:
            raise ValueError("accuracy 必须在 0~1")
        self._accuracy = float(value)

    @property
    def is_successful(self):            # 只读计算属性
        return self._accuracy >= 0.9


exp = Experiment("demo", 0.923)
print(exp.is_successful)                # True，不加括号
```

要点：

- 内部存储用 `_accuracy`，避免和 property 同名递归。
- 计算属性每次访问现算，不存冗余字段。

---

## @classmethod / @staticmethod

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    @classmethod
    def from_dict(cls, data):           # 工厂方法；cls 是类本身
        return cls(data["name"], data["accuracy"])

    @staticmethod
    def format_accuracy(value):         # 工具函数；不需要 self/cls
        return f"{value:.1%}"
```

| 类型 | 第一个参数 | 用途 |
|---|---|---|
| 实例方法 | `self` | 读写实例字段 |
| `@classmethod` | `cls` | 工厂方法、访问类状态 |
| `@staticmethod` | 无 | 纯工具函数 |

---

## dataclass 预览（W2）

```python
from dataclasses import dataclass

@dataclass
class Experiment:
    name: str
    model: str
    accuracy: float = 0.0


exp = Experiment("demo", "Qwen2.5-7B", 0.923)
print(exp)          # 自动生成 __repr__
```

W2 会用 dataclass 重构项目；现在先理解普通类，不然不知道 dataclass 省了什么。

---

## 选择速查

| 场景 | 选择 |
|---|---|
| 临时传参、结构不固定 | 字典 / 元组 |
| 固定字段 + 校验 + 行为 | 普通类 |
| 主要是数据容器 | dataclass（W2） |
| 需要多态 | 继承 |
| 需要复用配置/组件 | 组合 |
