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
> 先确认这个目录已经是一个 Git 仓库（Day 1 初始化过）。如果没有：`git init -b main`。

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

### 9.2 创建、切换、合并

```bash
# 确认当前在 main，且工作区干净
git status
git switch main

# 新建并切换到 feature/add-summary 分支
git switch -c feature/add-summary

# 在分支上改文件（这里用追加一行模拟）
echo "# summary feature" >> README.md

# 查看差异
git diff

# 提交
git add README.md
git commit -m "feat: add summary placeholder"

# 切回 main
git switch main

# 把分支合并进 main
git merge feature/add-summary

# 查看分支图
git log --oneline --graph --all

# 删除已合并的分支
git branch -d feature/add-summary
```

### 9.3 制造并解决一次冲突

冲突的本质：两个分支改了同一文件的同一区域，Git 不知道怎么合并，交给你决定。

```bash
# 1. 在 main 上创建练习文件
git switch main
cat > conflict.txt <<'TXT'
line 1
line 2
line 3
TXT
git add conflict.txt
git commit -m "chore: add conflict practice file"

# 2. 分支 A 改第二行
git switch -c feature/conflict-a
sed -i 's/line 2/line 2 from A/' conflict.txt
git add conflict.txt
git commit -m "feat: A changes line 2"

# 3. 回到 main，创建分支 B 改同一行
git switch main
git switch -c feature/conflict-b
sed -i 's/line 2/line 2 from B/' conflict.txt
git add conflict.txt
git commit -m "feat: B changes line 2"

# 4. 先合并 A（不会冲突）
git switch main
git merge feature/conflict-a

# 5. 再合并 B（会冲突）
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

解决：

```bash
# 6. 手动编辑 conflict.txt，删掉 <<<<<<< ======= >>>>>>> 标记，保留你想要的最终内容
#    例如保留 "line 2 from A and B" 或只保留一行
nano conflict.txt

# 7. 标记为已解决
git add conflict.txt

# 8. 完成合并提交
git commit -m "merge: resolve conflict between A and B"

# 9. 确认历史
git log --oneline --graph --all
```

冲突处理原则：

- **不要慌**：冲突不是错误，是 Git 让你做决定。
- 先理解两边各自改了什么，再决定最终内容。
- 解决后必须 `git add`，再 `git commit`。
- 如果搞砸了：`git merge --abort` 回到合并前。

### 9.4 撤销：`restore` / `reset` / `revert`

先分清三个区域：

```text
工作区  --git add-->  暂存区  --git commit-->  本地仓库
```

| 命令 | 作用 | 危险度 | 典型场景 |
|---|---|---|---|
| `git restore <file>` | 丢弃工作区改动，回到暂存区版本 | 中（改动会没） | 改乱了，不想要了 |
| `git restore --staged <file>` | 把文件移出暂存区，工作区不变 | 低 | `git add` 加错了 |
| `git reset --soft HEAD~1` | 撤销最后一次 commit，改动保留在暂存区 | 低 | 提交信息写错，想重提 |
| `git reset --mixed HEAD~1` | 撤销 commit，改动保留在工作区（默认） | 中 | 想重新挑文件提交 |
| `git reset --hard HEAD~1` | 撤销 commit，并丢弃所有改动 | **高** | 确定不要这次提交和改动 |
| `git revert <hash>` | 新建一个“反向提交”，抵消某次提交 | 低 | 已 push 的提交要撤销 |

练习：

```bash
# 1. 改一个文件，然后丢弃工作区改动
echo "temporary" >> README.md
git status
git restore README.md
git status                 # 应该干净

# 2. 改文件并 add，然后取消暂存
echo "temporary 2" >> README.md
git add README.md
git restore --staged README.md
git status                 # 改动还在工作区，但没暂存
git restore README.md      # 再丢弃

# 3. 提交一次，然后用 soft reset 撤销提交但保留改动
echo "soft reset practice" >> README.md
git add README.md
git commit -m "test: soft reset"
git reset --soft HEAD~1
git status                 # 改动仍在暂存区
git restore --staged README.md
git restore README.md

# 4. 提交一次，然后用 revert 安全撤销
echo "revert practice" >> README.md
git add README.md
git commit -m "test: revert practice"
git revert HEAD --no-edit
git log --oneline          # 会看到一条 Revert 提交
```

`reset --hard` 的警告：

```bash
# 危险演示：先确认你没有未提交的改动
git status
# git reset --hard HEAD~1   # 不要随便执行；会永久丢弃工作区和暂存区改动
```

如果误操作了 `reset --hard`：

- 立刻 `git reflog` 找到之前的 commit hash。
- `git reset --hard <hash>` 恢复。
- `reflog` 是本地操作记录，默认保留 90 天；越早恢复越好。

### 9.5 远程仓库：GitHub / Gitee

#### 1）配置 SSH key

```bash
# 如果 Day 1 已经生成过，可以复用；也可以单独生成一个给 GitHub 的
ssh-keygen -t ed25519 -C "your_email@example.com"

# 打印公钥，复制整行
cat ~/.ssh/id_ed25519.pub
```

- GitHub：Settings → SSH and GPG keys → New SSH key → 粘贴公钥。
- Gitee：设置 → SSH 公钥 → 添加公钥。

测试：

```bash
# GitHub；看到 "successfully authenticated" 就成功
ssh -T git@github.com

# Gitee
ssh -T git@gitee.com
```

#### 2）创建远程仓库并推送

在 GitHub/Gitee 网页上新建一个空仓库（不要勾选初始化 README），然后：

```bash
# 回到你的本地仓库
cd /root/aiinfra/S0-foundation/W1-environment-and-python/git-practice

# 添加远程地址；把 username/repo 换成你的
git remote add origin git@github.com:username/aiinfra-git-practice.git

# 查看远程
git remote -v

# 首次推送，并建立跟踪关系
git push -u origin main
```

以后再推送：

```bash
git push
```

拉取远程更新：

```bash
# --rebase 让本地提交排在远程提交之后，历史更干净
git pull --rebase
```

#### 3）网络问题的现实处理

- GitHub 在国内可能慢/不稳；W1 可以先用 Gitee 练手，后面 S4 做开源 PR 时再处理 GitHub 网络。
- 不要在主仓库里提交密钥、token、密码。
- 如果远程地址写错：`git remote set-url origin <新地址>`。
- 如果推送被拒（non-fast-forward）：先 `git pull --rebase`，解决冲突后再 `git push`；不要直接 `--force`。

### 9.6 标签

给 W1 项目打一个版本标签：

```bash
# 创建带说明的标签
git tag -a v0.1.0 -m "W1 experiment tracker v0.1.0"

# 查看标签
git tag

# 推送标签到远程
git push origin v0.1.0
```

### 9.7 Git 常见错误

| 现象 | 原因 | 解决 |
|---|---|---|
| `fatal: not a git repository` | 不在仓库目录 | `cd` 到仓库根目录 |
| `Your local changes would be overwritten by merge` | 工作区有未提交改动 | 先 commit 或 `git stash`，再 merge |
| `CONFLICT (content): Merge conflict in ...` | 两边改同一区域 | 手动解决，`git add`，`git commit` |
| `fatal: refusing to merge unrelated histories` | 两个仓库历史无关 | 确认后用 `git pull --allow-unrelated-histories` |
| `Updates were rejected because the remote contains work...` | 远程有你本地没有的提交 | `git pull --rebase` 后再 push |
| `detached HEAD` | 切到了某个 commit 而不是分支 | `git switch main` 或 `git switch -c new-branch` |
| 误删分支 | 分支指针没了 | `git reflog` 找到 hash，`git branch <name> <hash>` |

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