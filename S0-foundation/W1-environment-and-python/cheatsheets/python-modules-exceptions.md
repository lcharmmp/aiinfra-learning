# Python 模块 / 包 / 异常一页纸

---

## 模块与包

```text
math_utils.py                 -> 模块，模块名 math_utils
exp_tracker/                  -> 包，包名 exp_tracker
├── __init__.py
├── models.py
└── storage.py
```

- 一个 `.py` 文件 = 一个模块。
- 一个带 `__init__.py` 的目录 = 一个常规包。

---

## import 写法

```python
import math_utils                       # 用 math_utils.add(...)
from math_utils import add              # 直接用 add(...)
import math_utils as mu                 # 用 mu.add(...)
from exp_tracker import models          # 导入包内模块
from exp_tracker.models import Experiment
```

不推荐：

```python
from math_utils import *                # 容易命名冲突
```

---

## import 查找顺序

```python
import sys
print(sys.path)
```

1. 当前脚本所在目录（或 `python -m` 的当前工作目录）
2. `PYTHONPATH`
3. 标准库
4. `site-packages`

结论：

- 在 `project/` 下运行 `python3 main.py`，`project/` 在 `sys.path`，能导入 `exp_tracker`。
- 换目录运行脚本，导入和数据文件路径都可能出问题。

---

## `if __name__ == "__main__"`

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

- 直接运行文件：`__name__ == "__main__"`，执行 `main()`。
- 被 import：`__name__` 是模块名，不执行。

用途：自测代码、命令行入口。

---

## 绝对导入 vs 相对导入

```python
# 绝对导入（推荐，清晰）
from exp_tracker.models import Experiment
from exp_tracker.errors import ValidationError

# 相对导入（只能在包内模块使用）
from .models import Experiment
from .errors import ValidationError
```

相对导入直接运行会报：

```text
ImportError: attempted relative import with no known parent package
```

正确运行：

```bash
python3 -m exp_tracker.cli     # 从项目根目录
python3 main.py                # main.py 做入口
```

---

## `__init__.py` 与 `__all__`

```python
# exp_tracker/__init__.py
from .errors import ValidationError
from .models import Experiment
from .storage import JsonExperimentStore
from .service import ExperimentService

__all__ = [
    "ValidationError",
    "Experiment",
    "JsonExperimentStore",
    "ExperimentService",
]
```

- `__init__.py` 标记包，并可把常用名字提升到包级别。
- `__all__` 只影响 `from package import *`。
- `__init__.py` 保持轻量，不写业务逻辑。

---

## 循环导入

症状：

```text
ImportError: cannot import name 'X' from partially initialized module 'a'
```

处理顺序：

1. 检查职责是否没分清；能合并/拆分就重构。
2. 把共用代码移到第三个模块。
3. 延迟导入（把 import 放进函数）作为权宜之计。
4. `if TYPE_CHECKING:`（W2 类型标注时讲）。

---

## 异常层级

```text
BaseException
├── KeyboardInterrupt
├── SystemExit
└── Exception
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    └── ...
```

- 业务代码捕获 `Exception` 子类。
- 不捕获 `BaseException`。
- 不写裸 `except:`。

---

## try / except / else / finally

```python
def parse_learning_rate(text):
    try:
        value = float(text)
    except ValueError:
        print("不是数字")
        return None
    else:
        print("解析成功")
        return value
    finally:
        print("结束")          # 成功失败都执行
```

执行顺序：

```text
成功：try -> else -> finally
失败：try -> except -> finally
```

---

## 自定义异常

```python
class ExperimentTrackerError(Exception):
    """所有业务异常的基类。"""


class ValidationError(ExperimentTrackerError):
    """数据校验失败。"""


def validate_accuracy(value):
    if not 0 <= value <= 1:
        raise ValidationError(f"accuracy 越界: {value}")
    return value
```

好处：

- 名字即文档。
- 可以精确捕获，不误吞其他 `ValueError`。
- 可以建层级，上层统一兜底。

---

## 异常链

```python
class ConfigError(Exception):
    pass


def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"无法加载配置: {path}") from exc
```

- `raise ... from exc` 保留原始原因。
- 调试时看 `exc.__cause__` 和 traceback。

---

## EAFP vs LBYL

```python
# EAFP：先做，出错再处理
try:
    value = data["accuracy"]
except KeyError:
    value = 0.0

# LBYL：先检查，再做
if "accuracy" in data:
    value = data["accuracy"]
else:
    value = 0.0
```

两种都可以；不要用异常控制正常循环。

---

## pathlib + JSON 模板

```python
import json
from pathlib import Path

path = Path("data/experiments.json")

# 创建父目录
path.parent.mkdir(parents=True, exist_ok=True)

# 读文本
text = path.read_text(encoding="utf-8")

# 解析 JSON
data = json.loads(text) if text.strip() else []

# 写文本（原子写入的简化版）
tmp = path.with_name(path.name + ".tmp")
tmp.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
tmp.replace(path)
```

要点：

- 永远写 `encoding="utf-8"`。
- `ensure_ascii=False` 让中文可读。
- `tmp.replace(path)` 做原子替换。
- 读文件用 `try/except OSError`，解析 JSON 用 `try/except json.JSONDecodeError`。
