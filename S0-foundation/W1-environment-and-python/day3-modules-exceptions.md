# Day 3 · 模块 / 包 / 异常 / 项目骨架

> 阶段：S0 地基期 · W1 第 3 天
> 日期：2026-11-18（周三）
> 今日交付：能解释 `import` 的查找过程；能写自定义异常；能画出项目模块依赖图

---

## 0. 今日路线

| 时间 | 内容 | 产出 |
|---|---|---|
| 0:00 - 0:15 | 回顾 Day 2：继承/组合/property | 口述一遍 |
| 0:15 - 1:15 | 模块、包、`import`、`__name__`、绝对/相对导入 | 跑通 `examples/day3_modules_demo/` |
| 1:15 - 2:00 | 异常：`try/except/else/finally`、自定义异常、异常链 | 跑通 `examples/day3_exceptions_demo.py` |
| 2:00 - 2:40 | 读项目骨架，画依赖图 | 一张模块依赖图 |
| 2:40 - 3:00 | `compileall` 检查 + 小练习 | 项目骨架无语法错误 |
| 3:00 - 4:00 | 补课 + 复盘 | 今日复盘 |

---

## 1. 模块与包

### 1.1 什么是模块

一个 `.py` 文件就是一个模块。文件名（去掉 `.py`）就是模块名。

```text
math_utils.py   -> 模块名 math_utils
```

模块的好处：

- 把代码拆小，每个文件只负责一件事。
- 可以复用：别的文件 `import math_utils` 就能用里面的函数/类。
- 命名空间隔离：不同模块可以有同名函数。

### 1.2 什么是包

一个目录，如果里面有 `__init__.py`，就是一个“常规包”。目录名就是包名。

```text
exp_tracker/
├── __init__.py
├── models.py
├── storage.py
└── service.py
```

包的好处：

- 把多个模块组织成一个命名空间。
- 可以用 `from exp_tracker.models import Experiment`。
- `__init__.py` 可以控制“包对外暴露什么”。

> Python 3.3+ 还有“命名空间包”（没有 `__init__.py` 也能导入），但 W1 统一用常规包，行为更可控。

### 1.3 `import` 的几种写法

```python
# 1. 导入整个模块，使用时加模块名前缀
import math_utils
print(math_utils.add(1, 2))

# 2. 从模块导入指定名字，使用时不用前缀
from math_utils import add
print(add(1, 2))

# 3. 导入并起别名，避免名字冲突
import math_utils as mu
print(mu.add(1, 2))

# 4. 从包里导入模块
from exp_tracker import models

# 5. 从包的模块里导入类/函数
from exp_tracker.models import Experiment
```

不推荐：

```python
# 不推荐：星号导入会把所有公开名字倒进当前命名空间，容易冲突
from math_utils import *
```

### 1.4 `import` 到底去哪里找文件

Python 按 `sys.path` 的顺序查找模块。`sys.path` 通常包含：

1. 当前脚本所在目录（或 `python -m` 时的当前工作目录）。
2. `PYTHONPATH` 环境变量里的目录。
3. 标准库目录。
4. `site-packages`（pip 安装的第三方包）。

查看：

```bash
# python3：调用 Python 3 解释器
# -c "..."：command，直接执行引号里的 Python 代码，不生成 .py 文件
#   import sys：导入 sys 模块
#   sys.path：模块搜索路径列表
#   '\n'.join(...)：用换行符把列表元素拼成一个字符串
python3 -c "import sys; print('\n'.join(sys.path))"
```

关键结论：

- 你运行 `python3 main.py` 时，`main.py` 所在目录会被加到 `sys.path[0]`。
- 你在 `project/` 目录下运行 `python3 main.py`，`project/` 在路径里，所以 `import exp_tracker` 能找到 `project/exp_tracker/`。
- 如果你 `cd` 到别的目录再运行 `python3 /path/to/main.py`，`sys.path[0]` 是 `/path/to`，不是当前目录；这时相对路径/数据文件路径可能出错。

### 1.5 `if __name__ == "__main__"`

每个模块都有一个内置变量 `__name__`：

- 当文件被**直接运行**时，`__name__` 是 `"__main__"`。
- 当文件被**导入**时，`__name__` 是模块名（例如 `"math_utils"`）。

所以：

```python
# math_utils.py

def add(a, b):
    return a + b

# 只有直接运行 python math_utils.py 时才执行；被 import 时不执行
if __name__ == "__main__":
    # 这里放“自测代码”或“命令行入口”
    print(add(1, 2))   # 3
```

为什么要这个判断：

- 被别的模块导入时，不应该自动跑测试/打印/启动服务。
- 直接运行时，又能方便地自测。
- 项目的 `main.py` 用它作为程序入口。

### 1.6 绝对导入 vs 相对导入

**绝对导入**：从项目根/包名开始写完整路径。

```python
# 在 exp_tracker/service.py 里
from exp_tracker.models import Experiment
from exp_tracker.errors import ValidationError
```

**相对导入**：用 `.` 表示当前包，`..` 表示上一级包。

```python
# 在 exp_tracker/service.py 里
from .models import Experiment
from .errors import ValidationError
```

区别与坑：

- 相对导入只能在“包内模块”里用；直接 `python service.py` 运行会报 `ImportError: attempted relative import with no known parent package`。
- 正确运行方式：在项目根目录用 `python -m exp_tracker.cli`，或者让 `main.py` 做入口。
- W1 项目统一用**绝对导入**（`from exp_tracker.models import ...`），更直观；相对导入会在 W2 讲包设计时再对比。

### 1.7 `__init__.py` 和 `__all__`

`__init__.py` 可以做两件事：

1. 标记目录是包。
2. 决定 `from package import *` 时导出什么，或者把常用名字提前导入。

```python
# exp_tracker/__init__.py

# 把常用类提升到包级别，外部可以 from exp_tracker import Experiment
from .errors import ExperimentTrackerError, ValidationError
from .models import Experiment
from .storage import JsonExperimentStore
from .service import ExperimentService

# 定义 __all__：控制 from exp_tracker import * 时导出哪些名字
__all__ = [
    "ExperimentTrackerError",
    "ValidationError",
    "Experiment",
    "JsonExperimentStore",
    "ExperimentService",
]
```

注意：

- `__all__` 只影响 `import *`，不影响显式导入。
- `__init__.py` 里不要写太多业务逻辑，保持轻量。
- 循环导入时，`__init__.py` 里提前导入多个模块容易出问题；W2 会讲解决方案。

### 1.8 循环导入

```text
a.py 导入 b.py
b.py 导入 a.py
```

症状：

```text
ImportError: cannot import name 'X' from partially initialized module 'a'
```

解决顺序：

1. 先问：这两个模块是不是职责没分清？能合并/拆分吗？
2. 把“只被一方需要”的代码移到第三个模块。
3. 把导入放到函数内部（延迟导入），但这是权宜之计。
4. 用类型检查的 `if TYPE_CHECKING:`（W2 讲类型标注时再说）。

### 1.9 跑模块示例

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/examples

# 方式 1：用 -m 运行包内模块（推荐）
# python3 -m：-m = module，把后面的模块当作脚本运行，并保留包上下文
# day3_modules_demo.main：包名.模块名
# 这样相对导入 from .math_utils import ... 才能工作
python3 -m day3_modules_demo.main

# 方式 2：用 -m 运行整个包
# 包目录下有 __main__.py 时，python3 -m 包名 会执行它
# 这里 __main__.py 再调用 main.main()
python3 -m day3_modules_demo

# 方式 3：故意直接运行包内文件，观察相对导入报错
# 直接运行脚本时，Python 不知道父包是谁
# 预期：ImportError: attempted relative import with no known parent package
python3 day3_modules_demo/main.py

# 方式 4：进入 Python 交互环境（REPL）
# 不带文件名时，python3 进入交互模式，可以逐行执行
python3
```

交互环境里试：

```python
# 导入整个模块
import day3_modules_demo.math_utils as mu
print(mu.add(2, 3))          # 5
print(mu.multiply(2, 3))     # 6

# 从模块导入函数
from day3_modules_demo.math_utils import add
print(add(10, 20))           # 30

# 从包导入（看 __init__.py 暴露了什么）
from day3_modules_demo import add, multiply
print(add(1, 1), multiply(2, 2))
```

---

## 2. 异常处理

### 2.1 为什么需要异常

错误有两种处理方式：

- 返回错误码：`if result == -1: ...`，调用方容易忘记检查。
- 抛异常：错误发生时中断当前流程，交给能处理的地方。

Python 用异常。项目里必须处理的场景：

- 用户输入了 `abc` 当学习率 → `ValueError`
- JSON 文件损坏 → `json.JSONDecodeError`
- 实验 ID 不存在 → 自定义 `ExperimentNotFoundError`
- 文件没有写权限 → `PermissionError`

### 2.2 异常层级

Python 内置异常的大致层级（只列常用的）：

```text
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── IndexError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── ...
    └── ...
```

规则：

- 业务代码一般捕获 `Exception` 的子类。
- 不要捕获 `BaseException`（会把 `KeyboardInterrupt`、`SystemExit` 也吞掉）。
- 不要写裸 `except:`，至少写 `except Exception:`，更好的是捕获具体类型。

### 2.3 `try/except/else/finally`

```python
def parse_learning_rate(text):
    """把用户输入解析成 float；演示完整的异常结构。"""
    try:
        # 可能出错的代码
        value = float(text)
    except ValueError:
        # 只处理“转 float 失败”
        print(f"输入不是数字: {text!r}")
        return None
    else:
        # try 没有抛异常时执行
        print(f"解析成功: {value}")
        return value
    finally:
        # 无论成功失败都会执行；常用于清理资源
        print("parse_learning_rate 结束")

print(parse_learning_rate("0.0001"))  # 成功
print(parse_learning_rate("abc"))     # 失败
```

执行顺序：

```text
成功：try -> else -> finally
失败：try -> except -> finally
```

### 2.4 捕获具体异常

```python
# 不推荐：不知道哪里出错，也可能吞掉真正的 bug
try:
    value = int(text)
except:
    value = 0

# 推荐：只捕获你预期的错误
try:
    value = int(text)
except ValueError:
    value = 0
```

多个异常：

```python
try:
    # 可能抛 ValueError 或 TypeError
    result = int(text) / divisor
except (ValueError, TypeError) as exc:
    # 把原始异常信息带上，方便排查
    print(f"输入有误: {exc}")
except ZeroDivisionError as exc:
    print(f"除数不能为 0: {exc}")
```

### 2.5 `raise` 和自定义异常

```python
# 定义业务异常：继承 Exception（或项目基类）
class ValidationError(Exception):
    """数据校验失败。"""

def validate_accuracy(value):
    # 主动抛异常，而不是返回 None/False
    if not 0 <= value <= 1:
        raise ValidationError(f"accuracy 必须在 0 到 1 之间，收到 {value}")
    return value

try:
    validate_accuracy(1.5)
except ValidationError as exc:
    print("校验失败:", exc)
```

为什么要自定义异常：

- 调用方可以精确捕获 `ValidationError`，不会误吞 `ValueError`。
- 异常名字本身就是文档：看到 `ExperimentNotFoundError` 就知道发生了什么。
- 可以建层级：所有业务异常继承 `ExperimentTrackerError`，上层统一兜底。

### 2.6 异常链：`raise ... from ...`

当你捕获一个异常，又抛出另一个异常时，用 `from` 保留原始原因：

```python
import json

class ConfigError(Exception):
    """配置加载失败。"""

def load_config(path):
    try:
        # 可能抛 FileNotFoundError / json.JSONDecodeError
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        # 抛业务异常，同时保留原始异常链
        raise ConfigError(f"无法加载配置: {path}") from exc

try:
    load_config("not-exist.json")
except ConfigError as exc:
    print("业务错误:", exc)
    print("原始原因:", exc.__cause__)
```

好处：

- 上层看到的是“业务语义”（配置加载失败），不是底层实现细节。
- 调试时还能通过 `__cause__` / traceback 看到原始错误。

### 2.7 EAFP 风格

Python 社区常用 EAFP（Easier to Ask Forgiveness than Permission）：

```python
# EAFP：先做，出错再处理
try:
    value = data["accuracy"]
except KeyError:
    value = 0.0

# LBYL：先检查，再做（Look Before You Leap）
if "accuracy" in data:
    value = data["accuracy"]
else:
    value = 0.0
```

两种都可以；关键是**不要用异常控制正常流程**。比如用 `try/except` 做循环退出，会很难读。

### 2.8 跑异常示例

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python
python3 examples/day3_exceptions_demo.py
```

示例包含：

- `safe_divide`：捕获 `ZeroDivisionError`
- `parse_int`：捕获 `ValueError`，演示 `else/finally`
- `load_json`：捕获 `OSError` + `json.JSONDecodeError`，用 `raise ... from ...` 抛自定义 `ConfigError`
- `validate_accuracy`：自定义 `ValidationError`
- 一个 `main()` 演示所有场景

### 2.9 异常练习

1. 写 `parse_batch_size(text)`：
   - 转成 `int`
   - 如果小于等于 0，抛 `ValueError`
   - 如果输入不是整数，捕获 `ValueError`，重新抛出一个带说明的 `ValueError`
2. 写 `read_first_line(path)`：
   - 文件不存在时抛自定义 `FileMissingError`
   - 使用 `finally` 打印“尝试读取结束”
3. 解释：为什么 `except Exception:` 比裸 `except:` 好？什么时候仍然不该捕获 `Exception`？

---

## 3. 项目骨架

### 3.1 目录

```text
project/
├── README.md                 # 项目说明、运行方式、设计说明
├── main.py                   # 程序入口：调用 cli.run_cli()
├── requirements.txt          # 依赖说明（W1 只用标准库）
├── .gitignore                # 忽略缓存/虚拟环境/临时文件
├── data/
│   └── experiments.json      # JSON 数据文件（初始示例）
├── exp_tracker/              # 包
│   ├── __init__.py           # 包对外暴露的 API
│   ├── errors.py             # 自定义异常
│   ├── models.py             # Experiment 数据模型
│   ├── storage.py            # JSON 持久化
│   ├── service.py            # 业务逻辑
│   └── cli.py                # 命令行交互
└── tests/
    ├── __init__.py
    ├── test_models.py        # 模型校验/序列化测试
    ├── test_storage.py       # 存储读写/删除/损坏 JSON 测试
    └── test_service.py       # 业务汇总/删除/校验传播测试
```

### 3.2 每个文件的职责

| 文件 | 只负责 | 不负责 |
|---|---|---|
| `errors.py` | 定义异常类型 | 业务逻辑、I/O |
| `models.py` | 一条实验的数据、校验、序列化 | 文件读写、用户输入 |
| `storage.py` | JSON 文件读写、查找、删除 | 业务汇总、输入校验 |
| `service.py` | 业务用例：添加、列表、汇总、删除 | 直接读写文件、打印菜单 |
| `cli.py` | 菜单、输入、输出、错误提示 | 业务规则、JSON 细节 |
| `main.py` | 启动入口 | 任何业务逻辑 |

一句话：

```text
cli 负责“怎么问”，service 负责“做什么”，storage 负责“存哪里”，models 负责“长什么样”，errors 负责“怎么报错”。
```

### 3.3 依赖方向

```text
main.py
   │
   ▼
cli.py ───────▶ service.py ───────▶ storage.py ───────▶ models.py
   │                  │                    │                 │
   └──────────────────┴────────────────────┴─────────────────┘
                              errors.py（所有层都可以用）
```

关键规则：

- 依赖方向**单向**：cli → service → storage → models。
- models 不导入 storage/service/cli。
- storage 不导入 service/cli。
- errors 是叶子模块，谁都可以导入它，它不导入别人。
- 这样改一层不会牵动所有层，测试也容易替换。

### 3.4 先读骨架，不要急着写

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# 看目录
# find：查找文件/目录
# .：从当前目录开始
# -maxdepth 2：最多向下 2 层
# -type f：只匹配普通文件（f = file；目录是 d）
# |：管道，把左边输出作为右边输入
# sort：按字典序排序
find . -maxdepth 2 -type f | sort

# 只做语法检查，不运行
# python3 -m：把后面的模块当脚本运行（-m = module）
# compileall：标准库模块，递归编译 .py 文件检查语法
# -q：quiet，只输出错误，不打印每个被编译的文件
# exp_tracker main.py：要检查的包/文件
python3 -m compileall -q exp_tracker main.py

# echo：输出字符串
# $?：上一条命令的退出码，0 表示成功，非 0 表示失败
echo "compileall exit code: $?"
```

`compileall` 只检查语法，不执行代码。Day 4-5 再逐个实现。

### 3.5 读代码时问三个问题

对每个文件，读完回答：

1. 这个文件导入了谁？为什么需要它？
2. 这个文件对外提供什么名字（类/函数）？
3. 如果我要测试它，需要准备什么？（文件？临时目录？假对象？）

把答案写进 `notes/2026-11-18.md` 的“待我填写的笔记”。

### 3.6 今日小练习

1. 画出 `project/exp_tracker/` 的依赖图（用纸或 ASCII）。
2. 找出 `models.py` 里哪些方法不碰文件、哪些方法只做数据转换。
3. 找出 `storage.py` 里捕获了哪些异常，各自对应什么失败场景。
4. 解释：为什么 `cli.py` 不应该直接 `import json` 读写文件？

---

## 4. 今日复盘

打开 `notes/2026-11-18.md`，在“待我填写的笔记”里写三行：

```text
今天产出：
今天卡点：
明天第一件事：
```

自查：

- [ ] 能解释模块和包的区别
- [ ] 能解释 `if __name__ == "__main__"` 的作用
- [ ] 能说出绝对导入和相对导入的区别，以及相对导入什么时候会报错
- [ ] 能写出一个自定义异常，并用 `raise ... from ...` 保留原因
- [ ] 能画出 `cli → service → storage → models` 的依赖图
- [ ] 能独立写出一个包内模块，并用 `python -m` 正确运行

---

## 5. 明日预告

Day 4 开始写项目 part1：

- `errors.py`：设计异常层级
- `models.py`：`Experiment` 类、字段校验、`to_dict/from_dict`
- `storage.py`：JSON 读写、原子写入、查找、删除
- 手动 smoke test：存一条、读一条、删一条

---

## 6. 延伸阅读（可选）

- [Python 官方教程 · 模块](https://docs.python.org/zh-cn/3/tutorial/modules.html)
- [Python 官方教程 · 错误和异常](https://docs.python.org/zh-cn/3/tutorial/errors.html)
- [Real Python · Python Exceptions](https://realpython.com/python-exceptions/)

---

## 7. 复盘问答

> 这些问题来自今天的模块、导入、异常和项目骨架。工程里最容易出错的就是“边界”，下面按边界来答。

### Q1. `__init__.py` 到底有什么用？没有它会怎样？`__all__` 影响什么？

`__init__.py` 有两个作用：

1. 标记目录是**常规包**，让 `from package import module` 的行为更可控。
2. 在包被导入时执行一次，可以用来重新导出常用名字。

```python
# exp_tracker/__init__.py

# 把常用类提升到包级别
from .models import Experiment
from .service import ExperimentService

# __all__ 只影响 `from exp_tracker import *`
# 不影响显式导入 `from exp_tracker import Experiment`
__all__ = ["Experiment", "ExperimentService"]
```

没有 `__init__.py` 时，Python 3.3+ 可以把目录当“命名空间包”导入，但行为更隐晦，工具链（打包、类型检查、IDE）支持也不一致。学习项目统一用常规包。

`__all__` 的常见误解：

- 它**不限制** `from package import SpecificName`。
- 它只控制 `from package import *` 时导出哪些名字。
- 它也是文档：告诉读者这个包对外承诺哪些 API。

### Q2. `python3 main.py` 和 `python3 -m package.main` 到底差在哪？为什么相对导入会报错？

关键在 `sys.path[0]` 和“包上下文”。

```bash
# 方式 A：直接运行文件
# sys.path[0] = main.py 所在目录
python3 main.py

# 方式 B：用 -m 运行模块
# -m：module，把 package.main 当模块加载，并保留包上下文
# sys.path[0] = 当前工作目录（通常是项目根）
python3 -m exp_tracker.main
```

相对导入 `from .models import Experiment` 需要知道“当前包是谁”。直接运行 `main.py` 时，Python 把它当普通脚本，没有父包，所以报：

```text
ImportError: attempted relative import with no known parent package
```

工程建议：

- 应用入口用 `main.py` + **绝对导入**（`from exp_tracker.models import ...`）。
- 包内部模块可以用相对导入，但必须通过 `python3 -m package.module` 或入口文件运行。
- 不要一会儿绝对、一会儿相对；同一项目保持一致。

### Q3. 绝对导入和相对导入，工程上怎么选？

| 场景 | 建议 |
|---|---|
| 应用代码、入口、测试 | 绝对导入，路径清晰，IDE 跳转稳定 |
| 大型库内部、重构频繁 | 相对导入，移动包时少改 import |
| 学习项目 / W1 项目 | 统一绝对导入，减少困惑 |

绝对导入：

```python
from exp_tracker.models import Experiment
from exp_tracker.errors import ValidationError
```

相对导入：

```python
from .models import Experiment
from ..utils import load_config
```

注意：相对导入的层级越深越难读；超过两层（`..`）通常说明包结构该调整了。

### Q4. 循环导入的根因是什么？三种修法怎么选？

根因：模块 A 在初始化时导入 B，B 又导入 A，而 A 还没执行完，名字还不存在。

```text
a.py  import b
b.py  from a import X   # 此时 a 还没定义 X -> ImportError
```

修法优先级：

1. **重构职责**：把双方共用的代码移到第三个模块（推荐）。
2. **延迟导入**：把 import 放进函数内部，等真正调用时再导入（权宜之计）。
3. **类型检查导入**：只在类型标注时需要，用 `if TYPE_CHECKING:`（W2 类型标注会讲）。

```python
# 权宜之计：延迟导入
def build_service():
    # 只有调用这个函数时才导入，避免模块加载阶段循环
    from .storage import JsonExperimentStore
    return JsonExperimentStore("data/experiments.json")
```

延迟导入的代价：导入错误从启动时推迟到运行时；依赖关系变隐蔽。能重构就不要用它。

### Q5. `except Exception` 和裸 `except` 有什么区别？什么时候应该让异常继续往上抛？

- 裸 `except:` 会捕获 `BaseException`，包括 `KeyboardInterrupt`、`SystemExit`。用户按 Ctrl+C 时你的程序可能不退出。
- `except Exception:` 只捕获常规异常，至少不会吞掉退出信号。
- 更好的是捕获**具体异常**：`except ValueError:`、`except StorageError:`。

```python
# 不推荐：不知道哪里错，也可能吞掉 bug
try:
    value = int(text)
except:
    value = 0

# 推荐：只处理预期的错误
try:
    value = int(text)
except ValueError:
    value = 0
```

什么时候往上抛：

- 当前层不知道怎么处理（例如 storage 不知道怎么向用户展示错误）→ 包装后抛给上层。
- 当前层能恢复（例如输入格式错，重新询问）→ 当场处理。
- 程序 bug（例如 `TypeError`、`AttributeError`）→ 不要吞，让它暴露。

### Q6. `raise ... from ...` 的异常链怎么读？日志里怎么保留堆栈？

```python
class ConfigError(Exception):
    """配置加载失败。"""


def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        # 抛业务异常，同时用 from exc 保留原始原因
        raise ConfigError(f"无法加载配置: {path}") from exc
```

捕获后：

```python
try:
    load_config("not-exist.json")
except ConfigError as exc:
    # exc.__cause__ 是原始异常（FileNotFoundError / JSONDecodeError）
    print("业务错误:", exc)
    print("原始原因:", repr(exc.__cause__))
```

traceback 会显示两段：

```text
FileNotFoundError: ...
The above exception was the direct cause of the following exception:
ConfigError: 无法加载配置: not-exist.json
```

工程建议：

- 业务异常带上下文（哪个文件、哪条记录、哪个字段）。
- 原始异常保留在 `__cause__`，不要只写 `raise ConfigError(...)` 丢掉原因。
- 日志里记录完整 traceback（W2 的 `logging.exception` 会讲）。

### Q7. 为什么 `storage.py` 要把 `OSError`、`JSONDecodeError`、`ValidationError` 都包装成 `StorageError`？会不会丢失信息？

包装的目的不是“隐藏”，而是**统一边界**：

- `service` 和 `cli` 不需要知道底层是 JSON 还是数据库，也不需要 import `json`。
- 上层只需要捕获 `StorageError`，就能处理“存储不可用/数据损坏”。
- 原始异常通过 `from exc` 保留，调试时仍然能看到根因。

```python
try:
    text = self.data_file.read_text(encoding="utf-8")
except OSError as exc:
    # 把文件系统错误包装成业务异常，并保留原始原因
    raise StorageError(f"读取数据文件失败: {self.data_file}") from exc
```

什么时候不该包装：

- 程序员错误（例如给 `add()` 传了非 `Experiment` 对象）用 `TypeError`，不要包装成业务异常。
- 当前层能直接恢复的错误，不需要包装。

工程判断：**跨层边界包装，层内保持具体异常**。`storage` 内部可以捕获具体异常；对 `service` 暴露统一异常。
