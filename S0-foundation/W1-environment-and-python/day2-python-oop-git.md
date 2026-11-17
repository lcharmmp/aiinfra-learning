# Day 2 · 类与对象深化 / Git 分支、回滚、远程

> 阶段：S0 地基期 · W1 第 2 天
> 日期：2026-11-17（周二）
> 今日交付：能解释并手写继承/组合/property/魔术方法；在 `git-practice/` 完成分支、合并冲突、安全回滚

---

## 0. 今日路线

| 时间 | 内容 | 产出 |
|---|---|---|
| 0:00 - 0:20 | 回顾 Day 1：`__init__` / `self` / 实例属性 | 口述一遍 |
| 0:20 - 1:40 | `__repr__` / `__eq__` / 继承 / 组合 / property | 跑通 `examples/day2_oop_advanced.py` |
| 1:40 - 2:10 | `@classmethod` / `@staticmethod` / 类与字典的选择 | 完成 2 个练习 |
| 2:10 - 3:00 | Git 分支、合并、冲突、回滚、远程 | `git-practice/` 全套练完 |
| 3:00 - 4:00 | 补课 + 复盘 | 今日复盘 |

---

## 1. 先回顾：类到底在做什么

Day 1 的最小类：

```python
class ModelConfig:
    def __init__(self, name, hidden_size):
        self.name = name
        self.hidden_size = hidden_size

    def describe(self):
        return f"{self.name}: {self.hidden_size}"
```

三句话：

1. `class` 定义“模具”，`ModelConfig(...)` 用模具造“对象”。
2. `__init__` 在造对象时自动执行，负责把数据挂到 `self` 上。
3. `self` 就是“当前这个对象”；定义方法时写，调用时不用传。

今天在这个基础上加四件事：

- 对象怎么“打印”、怎么“比较”：`__repr__` / `__str__` / `__eq__`
- 类怎么复用：继承（is-a）和组合（has-a）
- 怎么控制属性读写：`@property`
- 怎么提供“工厂方法”和“工具函数”：`@classmethod` / `@staticmethod`

---

## 2. 魔术方法：`__repr__`、`__str__`、`__eq__`

### 2.1 默认打印很难看

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

exp = Experiment("qwen-lr1e-4", 0.923)

print(exp)
# <__main__.Experiment object at 0x7f8b1c2d3e50>
```

这个输出对调试几乎没用：看不出 `name` 和 `accuracy`。

### 2.2 `__repr__`：给开发者看的“精确表示”

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    def __repr__(self):
        # !r 表示用 repr() 格式化字符串，会带上引号，方便区分字符串和数字
        return f"Experiment(name={self.name!r}, accuracy={self.accuracy!r})"

exp = Experiment("qwen-lr1e-4", 0.923)
print(repr(exp))   # Experiment(name='qwen-lr1e-4', accuracy=0.923)
print(exp)         # 没有 __str__ 时，print 会退回用 __repr__
```

约定：

- `__repr__` 的目标是**无歧义**，最好能让你一眼看出怎么重建这个对象。
- 调试器、交互式解释器、容器打印（`print([exp1, exp2])`）都用 `__repr__`。
- 字符串字段用 `!r`，避免 `name=abc` 和 `name='abc'` 分不清。

### 2.3 `__str__`：给用户看的“可读描述”

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    def __repr__(self):
        return f"Experiment(name={self.name!r}, accuracy={self.accuracy!r})"

    def __str__(self):
        # 给用户看的格式：更友好，不追求可重建
        return f"{self.name}（准确率 {self.accuracy:.1%}）"

exp = Experiment("qwen-lr1e-4", 0.923)
print(str(exp))   # qwen-lr1e-4（准确率 92.3%）
print(exp)        # print 优先用 __str__
print([exp])      # 容器里用 __repr__
```

记忆：

```text
repr()  → 给开发者 / 调试 / 容器
str()   → 给用户 / print
没有 __str__ 时，print 退回 __repr__
```

### 2.4 `__eq__`：定义“相等”的含义

默认的 `==` 比较的是**是不是同一个对象**：

```python
a = Experiment("demo", 0.9)
b = Experiment("demo", 0.9)

print(a == b)   # False：两个不同对象
print(a is b)   # False
```

如果你认为“名字和准确率都一样，就是同一条实验”，就实现 `__eq__`：

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    def __eq__(self, other):
        # 1. 如果对方不是 Experiment，返回 NotImplemented，让 Python 尝试对方的 __eq__
        if not isinstance(other, Experiment):
            return NotImplemented
        # 2. 按业务字段比较
        return self.name == other.name and self.accuracy == other.accuracy

a = Experiment("demo", 0.9)
b = Experiment("demo", 0.9)
c = Experiment("demo", 0.8)

print(a == b)   # True
print(a == c)   # False
print(a == "demo")  # False（对方不是 Experiment，Python 最终返回 False）
```

注意：

- `is` 比较身份（内存里是不是同一个对象），`==` 比较值；不要混用。
- 浮点数直接用 `==` 比较可能有精度问题；项目里如果按 ID 比较，就不会有这个问题。Day 4 的 `Experiment.__eq__` 会用 `experiment_id`。
- 定义了 `__eq__` 后，对象默认不可哈希（不能放进 `set` 或当 `dict` 的 key）；需要的话再定义 `__hash__`。今天不展开。

### 2.5 小练习

给下面的 `Point` 类加 `__repr__` 和 `__eq__`：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

要求：

- `repr(Point(1, 2))` 输出 `Point(x=1, y=2)`
- `Point(1, 2) == Point(1, 2)` 为 `True`
- `Point(1, 2) == Point(2, 1)` 为 `False`

参考答案：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y
```

---

## 3. 继承：is-a 关系

### 3.1 为什么需要继承

项目里会有多种实验：

- 训练实验：有学习率、batch size
- 评测实验：有评测集、few-shot 数
- 压测实验：有并发数、TTFT、TPOT

它们都有共同字段：名字、模型、准确率、创建时间。共同逻辑不该复制三遍。

继承的做法：把共同部分放进基类，子类只写差异。

```text
Experiment（基类）
├── TrainingExperiment（训练实验）
├── EvalExperiment（评测实验）
└── BenchmarkExperiment（压测实验）
```

### 3.2 最小继承示例

```python
class Experiment:
    """所有实验的共同部分。"""

    def __init__(self, name, model, accuracy):
        self.name = name          # 实验名
        self.model = model        # 模型名
        self.accuracy = accuracy  # 准确率，0~1

    def summary(self):
        """返回一行摘要；子类可以覆盖。"""
        return f"{self.name} | {self.model} | acc={self.accuracy:.3f}"

class TrainingExperiment(Experiment):
    """训练实验：在基类基础上增加学习率和 batch size。"""

    def __init__(self, name, model, accuracy, learning_rate, batch_size):
        # super().__init__(...) 调用父类的构造方法，先把共同字段初始化好
        super().__init__(name, model, accuracy)
        # 再初始化子类特有字段
        self.learning_rate = learning_rate
        self.batch_size = batch_size

    def summary(self):
        # 先拿到父类的摘要，再追加子类字段
        base = super().summary()
        return f"{base} | lr={self.learning_rate} | bs={self.batch_size}"

# 基类对象
base_exp = Experiment("demo", "Qwen2.5-7B", 0.923)
print(base_exp.summary())

# 子类对象
train_exp = TrainingExperiment(
    "qwen-lr1e-4", "Qwen2.5-7B", 0.923,
    learning_rate=0.0001, batch_size=8,
)
print(train_exp.summary())
```

关键点：

- `class TrainingExperiment(Experiment):` 括号里是父类。
- `super().__init__(...)` 不是可选的：不调用的话，`name/model/accuracy` 不会初始化。
- 子类可以覆盖（override）父类方法；`super().summary()` 可以复用父类实现。
- 子类对象也是父类类型：`isinstance(train_exp, Experiment)` 为 `True`。

### 3.3 多态：同一个调用，不同行为

```python
experiments = [
    Experiment("base", "Qwen2.5-7B", 0.90),
    TrainingExperiment("train", "Qwen2.5-7B", 0.92, 1e-4, 8),
]

for exp in experiments:
    # 不关心具体类型，只调用统一的 summary()
    print(exp.summary())
```

这就是多态：调用方只依赖“有 `summary()` 方法”，不依赖具体子类。后面 PyTorch 的 `Dataset`、`nn.Module` 都是这个思路。

### 3.4 继承的边界

不要在需要“组合”的地方硬用继承。判断标准：

- **is-a**：训练实验是一种实验 → 继承合理。
- **has-a**：实验有一个模型配置 → 用组合。
- 如果两个类只是“共享几个字段”，但没有“是一种”的关系，优先组合。

---

## 4. 组合：has-a 关系

### 4.1 例子

```python
class ModelConfig:
    """模型配置；可以被多个实验复用。"""

    def __init__(self, model_name, precision="fp16"):
        self.model_name = model_name
        self.precision = precision

    def describe(self):
        return f"{self.model_name} ({self.precision})"

class EvalExperiment:
    """评测实验：持有一个 ModelConfig，而不是继承它。"""

    def __init__(self, name, config, accuracy):
        self.name = name
        self.config = config      # 组合：EvalExperiment has-a ModelConfig
        self.accuracy = accuracy

    def summary(self):
        # 通过持有的对象调用它的方法
        return f"{self.name} | {self.config.describe()} | acc={self.accuracy:.3f}"

config = ModelConfig("Qwen2.5-7B-Instruct", "awq")
exp = EvalExperiment("awq-eval", config, 0.917)
print(exp.summary())
```

组合的好处：

- 配置可以被多个实验共享。
- 替换配置很容易：换一个 `ModelConfig` 对象即可。
- 不会出现“评测实验是一种模型配置”这种别扭的继承关系。

### 4.2 项目里的组合

Day 4 的项目会这样组织：

```text
ExperimentService  has-a  JsonExperimentStore
JsonExperimentStore has-a  Path
Experiment         has-a  experiment_id / 字段
```

`Service` 不继承 `Store`，而是持有一个 `Store`；这样测试时可以换成内存 store，业务逻辑不用改。

---

## 5. `@property`：控制属性读写

### 5.1 只读属性

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    @property
    def is_successful(self):
        """只读属性：像访问字段一样访问方法。"""
        return self.accuracy >= 0.9

exp = Experiment("demo", 0.923)
print(exp.is_successful)   # True，注意没有括号
```

### 5.2 带校验的 setter

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        # 这里会触发 accuracy 的 setter，而不是直接创建实例属性
        self.accuracy = accuracy

    @property
    def accuracy(self):
        """读取 accuracy 时调用。"""
        return self._accuracy

    @accuracy.setter
    def accuracy(self, value):
        """设置 accuracy 时调用；在这里做校验。"""
        if not isinstance(value, (int, float)):
            raise ValueError("accuracy 必须是数字")
        if not 0 <= value <= 1:
            raise ValueError("accuracy 必须在 0 到 1 之间")
        self._accuracy = float(value)   # 真正的存储放在 _accuracy

exp = Experiment("demo", 0.923)
print(exp.accuracy)      # 0.923

try:
    exp.accuracy = 1.5   # 触发校验，抛 ValueError
except ValueError as exc:
    print("设置失败:", exc)
```

为什么要用 `_accuracy`：

- 属性名 `accuracy` 已经被 `@property` 占用；内部存储换一个名字，避免无限递归。
- `_` 开头表示“内部使用”，外部不要直接改。

### 5.3 计算属性

```python
class DatasetConfig:
    def __init__(self, num_samples, seq_len):
        self.num_samples = num_samples
        self.seq_len = seq_len

    @property
    def total_tokens(self):
        """每次访问都现算，不存储冗余字段。"""
        return self.num_samples * self.seq_len

cfg = DatasetConfig(1000, 512)
print(cfg.total_tokens)   # 512000
```

---

## 6. `@classmethod` 和 `@staticmethod`

### 6.1 `@classmethod`：工厂方法

```python
class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    @classmethod
    def from_dict(cls, data):
        """从字典创建对象；cls 是类本身，子类调用时会得到子类。"""
        return cls(data["name"], data["accuracy"])

exp = Experiment.from_dict({"name": "demo", "accuracy": 0.923})
print(exp.name, exp.accuracy)
```

为什么用 `cls` 而不是写死 `Experiment(...)`：

```python
class TrainingExperiment(Experiment):
    def __init__(self, name, accuracy, lr):
        super().__init__(name, accuracy)
        self.lr = lr

    @classmethod
    def from_dict(cls, data):
        # cls 是 TrainingExperiment，所以会创建 TrainingExperiment 而不是 Experiment
        return cls(data["name"], data["accuracy"], data["lr"])
```

### 6.2 `@staticmethod`：放在类里的工具函数

```python
class Experiment:
    @staticmethod
    def format_accuracy(value):
        """和具体实例无关，只是逻辑上属于 Experiment 的工具。"""
        return f"{value:.1%}"

print(Experiment.format_accuracy(0.923))  # 92.3%
```

### 6.3 三者怎么选

| 方法类型 | 第一个参数 | 需要实例数据？ | 需要类数据/构造子类？ | 典型用途 |
|---|---|---|---|---|
| 实例方法 | `self` | 是 | 否 | 读写实例字段、业务行为 |
| `@classmethod` | `cls` | 否 | 是 | `from_dict`、`from_json` 等工厂 |
| `@staticmethod` | 无 | 否 | 否 | 格式化、校验、纯工具函数 |

---

## 7. 类、字典、dataclass 怎么选

| 场景 | 选择 | 原因 |
|---|---|---|
| 临时传几个参数、结构不固定 | 字典 / 元组 | 轻量，不用定义类 |
| 有固定字段 + 校验 + 行为 | 普通类 | 数据和行为绑定 |
| 主要是数据容器，少量方法 | `@dataclass`（W2） | 自动生成 `__init__/__repr__/__eq__` |
| 需要继承/多态 | 类 | 子类覆盖方法 |
| 需要被多个对象共享的配置 | 组合一个配置类 | 避免继承层级膨胀 |

W1 先用普通类把原理吃透；W2 再用 dataclass 重构，你会更清楚 dataclass 帮你省了什么。

---

## 8. 跑今天的示例文件

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python

# 运行 OOP 进阶示例
python3 examples/day2_oop_advanced.py
```

示例文件包含：

- `Experiment` 基类：`__repr__` / `__str__` / `__eq__` / `@property`
- `TrainingExperiment` 子类：继承 + `super().__init__`
- `ModelConfig` + `EvalExperiment`：组合
- `@classmethod` / `@staticmethod`
- 一个 `if __name__ == "__main__":` 的演示区

读完后做练习：

```python
# 练习 1：给 Experiment 加一个 @property
#   is_successful：accuracy >= 0.9 时返回 True
#
# 练习 2：写一个 BenchmarkExperiment(Experiment) 子类
#   额外字段：concurrency、ttft_ms、tpot_ms
#   summary() 在父类基础上追加这三个字段
#
# 练习 3：给 Experiment 加 from_dict 类方法
#   输入 {"name": ..., "model": ..., "accuracy": ...}
#   返回 Experiment 对象
#
# 练习 4：解释为什么 EvalExperiment 用组合而不是继承 ModelConfig
```

---

## 9. Git 深化：分支、合并、冲突、回滚、远程

> 所有命令都在 `/root/aiinfra/S0-foundation/W1-environment-and-python/git-practice/` 里练。
> 如果这个目录还不是 Git 仓库：
>
> ```bash
> # git init：创建仓库
> # -b main：初始分支名设为 main（-b = --initial-branch，Git 2.28+）
> # 旧版 Git 用：git init && git branch -m main
> git init -b main
> ```

### 9.1 分支是什么

分支是一条独立的提交线：

```text
main:     A --- B --- C
                       \
feature:                D --- E
```

- `main` 保持可运行。
- 新功能在 `feature` 分支开发。
- 开发完合并回 `main`。
- 出问题只影响分支，不影响主线。

Git 里有一个特殊指针 `HEAD`，它指向“你当前所在的分支或提交”：

```text
HEAD -> main -> C
```

切换分支时，`HEAD` 会跟着移动；这也是为什么 `git status` 第一行会显示 `On branch main`。

### 9.2 创建、切换、合并

```bash
# git status：查看当前分支，以及暂存区/工作区状态
git status

# git switch：切换分支
# main：目标分支名
git switch main

# git switch -c：创建新分支并立即切换
# -c：--create，创建
# feature/add-summary：新分支名
#   / 只是命名分隔符，方便分类，不是目录
git switch -c feature/add-summary

# echo：把字符串输出到标准输出
# >> README.md：追加到文件末尾
#   >  是覆盖写入（会清空原文件）
#   >> 是追加写入（保留原内容）
echo "# summary feature" >> README.md

# git diff：显示“工作区 vs 暂存区”的差异
# 也就是还没 git add 的改动
git diff

# git add：把文件加入暂存区
# README.md：目标文件
git add README.md

# git commit：把暂存区生成一个提交
# -m：直接在命令行给提交说明
git commit -m "feat: add summary placeholder"

# git switch main：切回 main 分支
git switch main

# git merge：把指定分支合并进“当前分支”
# feature/add-summary：要合并的分支
# 如果 main 在分叉后没有新提交，默认是 fast-forward（快进），
# 只移动指针，不产生额外的 merge commit。
# 想强制保留分支历史，用 --no-ff（no fast-forward）。
git merge feature/add-summary

# git log：查看历史
# --oneline：一行一个提交（短哈希 + 说明）
# --graph：用 ASCII 字符画分支/合并图
# --all：显示所有分支，不只当前分支
git log --oneline --graph --all

# git branch：管理分支
# -d：--delete，删除已合并的分支；未合并时 Git 会拒绝
#     强制删除用 -D（--delete --force），会丢提交，慎用
# feature/add-summary：要删除的分支名
git branch -d feature/add-summary
```

分支命令参数速查：

| 命令 | 参数解释 | 作用 |
|---|---|---|
| `git branch` | 无参数：列本地分支 | 查看分支 |
| `git branch -a` | `-a`：--all，包含远程分支 | 查看所有分支 |
| `git branch -v` | `-v`：verbose，显示每个分支最后一次提交 | 看分支状态 |
| `git switch main` | `main`：目标分支 | 切换分支 |
| `git switch -c new` | `-c`：--create，创建并切换 | 新建分支 |
| `git merge feature` | `feature`：要合并进来的分支 | 合并到当前分支 |
| `git merge --no-ff feature` | `--no-ff`：禁止快进，强制生成 merge commit | 保留分支历史 |
| `git branch -d feature` | `-d`：--delete，仅删已合并分支 | 安全删除 |
| `git branch -D feature` | `-D`：--delete --force，强制删除 | 丢弃未合并分支 |
| `git branch -m new` | `-m`：--move，重命名当前分支 | 改分支名 |
| `git branch -M main` | `-M`：--move --force，强制重命名 | 把 master 改成 main |

### 9.3 制造并解决一次冲突

冲突的本质：两个分支改了同一文件的同一区域，Git 不知道怎么合并，交给你决定。

```bash
# 1. 在 main 上创建练习文件
# git switch main：确保当前在 main
git switch main

# cat > conflict.txt <<'TXT'：
#   cat：输出标准输入/文件内容
#   > conflict.txt：覆盖写入
#   <<'TXT'：here-document，直到单独一行 TXT 结束
#   'TXT' 加引号：不做变量替换
cat > conflict.txt <<'TXT'
line 1
line 2
line 3
TXT

# git add：暂存新文件
git add conflict.txt

# git commit：提交
# -m：提交说明
git commit -m "chore: add conflict practice file"

# 2. 分支 A 改第二行
# git switch -c：创建并切换到 feature/conflict-a
git switch -c feature/conflict-a

# sed：流编辑器
# -i：in-place，直接改文件
# 's/line 2/line 2 from A/'：把每行第一个 line 2 替换成 line 2 from A
sed -i 's/line 2/line 2 from A/' conflict.txt

# 暂存 + 提交
git add conflict.txt
git commit -m "feat: A changes line 2"

# 3. 回到 main，创建分支 B 改同一行
git switch main
git switch -c feature/conflict-b

# 同样用 sed -i 改同一行
sed -i 's/line 2/line 2 from B/' conflict.txt
git add conflict.txt
git commit -m "feat: B changes line 2"

# 4. 先合并 A（不会冲突）
git switch main
git merge feature/conflict-a

# 5. 再合并 B（会冲突）
# 因为 B 和 A 改了同一行，Git 无法自动决定保留哪个
git merge feature/conflict-b
```

此时 `git status` 会显示 `both modified: conflict.txt`，文件内容变成：

```text
line 1
<<<<<<< HEAD
line 2 from A
=======
line 2 from B
>>>>>>> feature/conflict-b
line 3
```

- `<<<<<<< HEAD` 到 `=======` 之间：当前分支（main，已合并 A）的内容。
- `=======` 到 `>>>>>>> feature/conflict-b` 之间：要合并进来的分支 B 的内容。

解决：

```bash
# 6. 手动编辑 conflict.txt，删掉三个冲突标记，保留最终内容
# nano：简单文本编辑器；Ctrl+O 保存，Ctrl+X 退出
nano conflict.txt

# 7. git add：告诉 Git“这个文件的冲突已经解决”
# 解决后必须 add，否则 Git 仍认为文件处于冲突状态
git add conflict.txt

# 8. git commit：完成这次合并提交
# -m：提交说明；这里没有 -m 的话 Git 会打开编辑器
git commit -m "merge: resolve conflict between A and B"

# 9. 确认历史
git log --oneline --graph --all
```

冲突处理原则：

- **不要慌**：冲突不是错误，是 Git 让你做决定。
- 先理解两边各自改了什么，再决定最终内容。
- 解决后必须 `git add`，再 `git commit`。
- 如果搞砸了：

```bash
# git merge --abort
# --abort：中止当前这次 merge，把工作区恢复到合并前的状态
git merge --abort
```

### 9.4 撤销：`restore` / `reset` / `revert`

先分清三个区域：

```text
工作区  --git add-->  暂存区/索引  --git commit-->  本地仓库
```

| 命令 | 参数解释 | 作用 | 危险度 |
|---|---|---|---|
| `git restore file` | `restore`：恢复；`file`：目标文件 | 丢弃工作区改动，回到暂存区版本 | 中 |
| `git restore --staged file` | `--staged`：只恢复暂存区 | 取消暂存，工作区不变 | 低 |
| `git reset --soft HEAD~1` | `--soft`：只移动 HEAD，不动暂存区/工作区；`HEAD~1`：上一个提交 | 撤销 commit，改动留在暂存区 | 低 |
| `git reset --mixed HEAD~1` | `--mixed`：默认模式，移动 HEAD 并重置暂存区，保留工作区 | 撤销 commit，改动留在工作区 | 中 |
| `git reset --hard HEAD~1` | `--hard`：HEAD、暂存区、工作区全部重置 | 撤销 commit 并丢弃改动 | **高** |
| `git revert <hash>` | `revert`：生成一个反向提交；`<hash>`：目标提交 | 安全撤销某次提交，不改历史 | 低 |

关于 `HEAD~1`：

- `HEAD`：当前提交。
- `HEAD~1`：当前提交的第一个父提交，也就是“上一个提交”。
- `HEAD^`：和 `HEAD~1` 等价。
- `HEAD~2`：往上两个提交。
- `HEAD~1` 不是“回退 1 个文件”，而是“回退 1 个提交”。

练习：

```bash
# 1. 改一个文件，然后丢弃工作区改动
# echo "temporary" >> README.md：追加一行
echo "temporary" >> README.md

# git status：应看到 README.md 被修改
git status

# git restore README.md
# restore：把工作区文件恢复到暂存区版本
# README.md：目标文件
# 注意：这会丢弃你刚才的改动
git restore README.md

# 再看状态，应该干净
git status

# 2. 改文件并 add，然后取消暂存
echo "temporary 2" >> README.md
git add README.md

# git restore --staged README.md
# --staged：只把文件从暂存区移出，工作区改动保留
git restore --staged README.md

# git status：改动还在工作区，但没暂存
git status

# 再丢弃工作区改动
git restore README.md

# 3. 提交一次，然后用 soft reset 撤销提交但保留改动
echo "soft reset practice" >> README.md
git add README.md
git commit -m "test: soft reset"

# git reset --soft HEAD~1
# --soft：只把当前分支指针回退到 HEAD~1
#         暂存区和工作区都不动，所以改动仍然在暂存区
git reset --soft HEAD~1

# 看状态：改动仍在暂存区
git status

# 取消暂存并丢弃改动
git restore --staged README.md
git restore README.md

# 4. 提交一次，然后用 revert 安全撤销
echo "revert practice" >> README.md
git add README.md
git commit -m "test: revert practice"

# git revert HEAD --no-edit
# revert：创建一个“反向提交”，抵消 HEAD 的改动
# HEAD：要撤销的提交
# --no-edit：使用默认的 Revert 提交说明，不打开编辑器
git revert HEAD --no-edit

# 查看历史：会看到一条 Revert 提交
git log --oneline
```

`reset --hard` 的警告：

```bash
# 危险演示：先确认你没有未提交的改动
git status

# git reset --hard HEAD~1
# --hard：把 HEAD、暂存区、工作区全部退回到 HEAD~1
# 你未提交的改动会永久丢失（普通文件系统层面）
# 不要随便执行
# git reset --hard HEAD~1
```

如果误操作了 `reset --hard`：

```bash
# git reflog：reference log，记录 HEAD 的移动历史
# 找到误操作前的 commit hash
git reflog

# git reset --hard <hash>
# 把 HEAD、暂存区、工作区恢复到那个提交
git reset --hard <hash>
```

`reflog` 是本地操作记录，默认保留 90 天；越早恢复越好。

### 9.5 远程仓库：GitHub / Gitee

> Day 1 的 4.7 节有更完整的“从零推送到 GitHub”图文步骤；这里补充命令参数和日常协作。

#### 9.5.1 配置 SSH key

```bash
# ssh-keygen：生成 SSH 密钥对
# -t ed25519：密钥类型；ed25519 比 RSA 更短、更安全
# -C "your_email@example.com"：给公钥加注释，方便辨认
# 交互提示直接回车用默认路径；建议设置 passphrase
ssh-keygen -t ed25519 -C "your_email@example.com"

# cat：打印文件内容
# ~/.ssh/id_ed25519.pub：公钥文件；.pub 结尾才是公钥
cat ~/.ssh/id_ed25519.pub
```

- GitHub：Settings → SSH and GPG keys → New SSH key → 粘贴公钥。
- Gitee：设置 → SSH 公钥 → 添加公钥。

测试：

```bash
# ssh：SSH 客户端
# -T：不分配伪终端（test only）
# git@github.com：GitHub 的 SSH 地址，用户名固定是 git
ssh -T git@github.com

# Gitee 同理
ssh -T git@gitee.com
```

看到 `successfully authenticated` 就成功。

如果 22 端口被阻断：

```bash
# -p 443：连接 443 端口，绕过对 22 端口的封锁
# git@ssh.github.com：GitHub 的 443 端口 SSH 入口
ssh -T -p 443 git@ssh.github.com
```

#### 9.5.2 添加远程、首次推送

在 GitHub/Gitee 网页上新建一个空仓库（不要勾选初始化 README），然后：

```bash
# cd：回到你的本地仓库
cd /root/aiinfra/S0-foundation/W1-environment-and-python/git-practice

# git remote：管理远程仓库
# add：新增一个远程
# origin：远程名，Git 约定俗成的默认名
# git@github.com:username/repo.git：SSH 远程地址
#   把 username/repo 换成你的用户名和仓库名
git remote add origin git@github.com:username/aiinfra-git-practice.git

# -v：verbose，显示 fetch 和 push 两个 URL
git remote -v

# git push：上传本地提交
# -u：--set-upstream，把本地 main 和远程 origin/main 关联
#     以后直接 git push / git pull 就行
# origin：远程名
# main：本地分支名
git push -u origin main
```

以后再推送：

```bash
# 因为前面用了 -u，这里不需要再写 origin main
git push
```

拉取远程更新：

```bash
# git pull：fetch（下载远程提交）+ 整合
# --rebase：把本地提交“重放”到远程最新提交之后
#           不产生多余的 merge commit
git pull --rebase
```

#### 9.5.3 常见远程问题

```bash
# 远程地址写错：修改 URL
# set-url：设置远程 URL
git remote set-url origin git@github.com:username/new-repo.git

# 查看远程名和 URL
git remote -v

# 删除一个远程（确认不再需要时）
# remove：删除远程配置，不会删除远程仓库本身
git remote remove origin
```

- GitHub 在国内可能慢/不稳；W1 可以先用 Gitee 练手。
- 不要提交密钥、token、密码。
- 推送被拒（non-fast-forward）：先 `git pull --rebase`，解决冲突后再 `git push`；不要直接 `--force`。

### 9.6 标签

给 W1 项目打一个版本标签：

```bash
# git tag：管理标签
# -a：annotated，创建带说明的“附注标签”
# v0.1.0：标签名
# -m：标签说明
git tag -a v0.1.0 -m "W1 experiment tracker v0.1.0"

# 不带参数：列出所有标签
git tag

# 查看某个标签的详细信息
git show v0.1.0

# git push：推送
# origin：远程名
# v0.1.0：标签名
# 注意：普通 git push 不会自动推送标签，必须显式指定
git push origin v0.1.0

# 一次性推送所有标签（可选）
# --tags：把所有标签都推到远程；不加则只推当前分支的提交
git push --tags
```

### 9.7 Git 常见错误

| 现象 | 原因 | 解决 |
|---|---|---|
| `fatal: not a git repository` | 不在仓库目录 | `cd` 到仓库根目录 |
| `Your local changes would be overwritten by merge` | 工作区有未提交改动 | 先 `git commit`，或 `git stash`（暂存工作区改动）后再 merge |
| `CONFLICT (content): Merge conflict in ...` | 两边改同一区域 | 手动解决，`git add`，`git commit` |
| `fatal: refusing to merge unrelated histories` | 两个仓库历史无关 | 确认后用 `git pull --allow-unrelated-histories`（允许合并无关历史） |
| `Updates were rejected because the remote contains work...` | 远程有你本地没有的提交 | `git pull --rebase` 后再 push |
| `detached HEAD` | 切到了某个 commit 而不是分支 | `git switch main` 或 `git switch -c new-branch` |
| 误删分支 | 分支指针没了 | `git reflog` 找到 hash，`git branch <name> <hash>` |
| `remote origin already exists` | 已经添加过同名远程 | `git remote set-url origin <新地址>` |
| `Permission denied (publickey)` | 公钥没配好 | `ssh -T git@github.com` 测试；`ssh-add ~/.ssh/id_ed25519` |
| `src refspec main does not match any` | 本地没有 main 分支/没有提交 | `git branch -M main`；确认有提交 |

> 记忆：`-b` initial-branch，`-c` create，`-d` delete，`-D` force delete，`-m` message/move，`-M` force move，`-u` set-upstream，`-v` verbose，`--staged` 暂存区，`--hard` 连工作区一起重置。

---

## 10. 今日复盘

打开 `notes/2026-11-17.md`，在“待我填写的笔记”里写三行：

```text
今天产出：
今天卡点：
明天第一件事：
```

自查：

- [ ] 能不看代码，写出 `__repr__` / `__eq__`
- [ ] 能解释 `super().__init__` 的作用
- [ ] 能各举一个继承和组合的例子
- [ ] 能解释 `@property` 为什么内部用 `_accuracy`
- [ ] 完成一次分支合并
- [ ] 完成一次冲突解决
- [ ] 能说出 `reset --soft` / `--mixed` / `--hard` 的区别

---

## 11. 明日预告

Day 3 进入“工程化”：

- 模块与包：`import` 到底怎么找文件
- `if __name__ == "__main__"` 的真实用途
- 绝对导入 vs 相对导入
- 异常处理：`try/except/else/finally`、自定义异常、`raise ... from ...`
- 读懂 `project/exp_tracker/` 的骨架

---

## 12. 延伸阅读（可选）

- [Python 官方教程 · 类](https://docs.python.org/zh-cn/3/tutorial/classes.html)
- [Pro Git 中文版 · 分支](https://git-scm.com/book/zh/v2/Git-%E5%88%86%E6%94%AF-%E5%88%86%E6%94%AF%E7%AE%80%E4%BB%8B)
- [Pro Git 中文版 · 撤销操作](https://git-scm.com/book/zh/v2/Git-%E5%9F%BA%E7%A1%80-%E6%92%A4%E9%94%80%E6%93%8D%E4%BD%9C)