# Day 4 · 项目 part1：errors / models / storage

> 阶段：S0 地基期 · W1 第 4 天
> 日期：2026-11-19（周四）
> 今日交付：能往 JSON 存一条实验、读出来、按 ID 查找、删除；每完成一个文件提交一次 Git

---

## 0. 今日路线

| 时间 | 内容 | 产出 |
|---|---|---|
| 0:00 - 0:15 | 读需求、字段表、校验规则 | 一张字段/规则清单 |
| 0:15 - 0:40 | 实现 `errors.py` | 异常层级 + 第一次提交 |
| 0:40 - 1:50 | 实现 `models.py` | `Experiment` 类 + 校验 + 序列化 |
| 1:50 - 2:50 | 实现 `storage.py` | JSON 读写 + 查找/删除 |
| 2:50 - 3:00 | 手动 smoke test + 提交 | 存/读/删跑通 |
| 3:00 - 4:00 | 补课 + 复盘 | 今日复盘 |

> 重要：先自己写。卡住 15 分钟再看 `project/` 里的参考实现；看懂后关掉文件，自己重敲一遍。

---

## 1. 先读需求

### 1.1 一条实验记录有哪些字段

| 字段 | 类型 | 规则 | 默认值 |
|---|---|---|---|
| `experiment_id` | str | 唯一；不传自动生成 8 位十六进制 | `uuid4().hex[:8]` |
| `name` | str | 非空，≤ 50 字符 | 无（必填） |
| `model` | str | 非空 | 无（必填） |
| `learning_rate` | float | > 0 | 无（必填） |
| `batch_size` | int | > 0 | 无（必填） |
| `accuracy` | float | 0 ≤ x ≤ 1 | 无（必填） |
| `loss` | float | ≥ 0 | 无（必填） |
| `notes` | str | ≤ 500 字符 | `""` |
| `created_at` | str | ISO 8601 | 当前时间 |

### 1.2 JSON 文件长什么样

```json
[
  {
    "experiment_id": "demo0001",
    "name": "qwen2.5-7b-lr1e-4",
    "model": "Qwen2.5-7B-Instruct",
    "learning_rate": 0.0001,
    "batch_size": 8,
    "accuracy": 0.923,
    "loss": 0.214,
    "notes": "S0 示例数据",
    "created_at": "2026-11-16T09:00:00"
  }
]
```

### 1.3 三层职责

```text
models.py    一条记录长什么样、怎么校验、怎么转字典
storage.py   JSON 文件怎么读写、怎么查找/删除
errors.py    出错时抛什么异常
```

今天不写 `service.py` 和 `cli.py`。

---

## 2. 实现顺序

按依赖方向写，先把叶子模块写好：

```text
errors.py  ->  models.py  ->  storage.py
```

每完成一个文件：

```bash
git add <file>
git commit -m "feat: ..."
```

---

## 3. `errors.py`：异常层级

### 3.1 为什么先写异常

`models.py` 和 `storage.py` 都会抛异常。先把异常类型定好，后面直接引用，不会出现“先写了一个 `ValueError`，后来又改成自定义异常”的返工。

### 3.2 设计

```text
ExperimentTrackerError       所有业务异常的基类
├── ValidationError          数据不合法
├── StorageError             文件读写/JSON 损坏/ID 重复
└── ExperimentNotFoundError  按 ID 找不到
```

### 3.3 代码骨架

```python
class ExperimentTrackerError(Exception):
    """所有 exp_tracker 业务异常的基类。"""

class ValidationError(ExperimentTrackerError):
    """数据校验失败。"""

class StorageError(ExperimentTrackerError):
    """存储层失败。"""

class ExperimentNotFoundError(ExperimentTrackerError):
    """按 ID 找不到实验。"""
```

### 3.4 三个设计问题

1. **为什么继承 `Exception` 而不是 `BaseException`？**
   `BaseException` 包含 `KeyboardInterrupt`、`SystemExit`；业务代码不应该吞掉这些退出信号。

2. **为什么要有共同基类？**
   CLI 可以统一 `except ExperimentTrackerError` 打印友好提示；测试也可以按需捕获更具体的子类。

3. **什么时候用内置异常？**
   程序员错误（例如给 `store.add()` 传了非 `Experiment` 对象）用 `TypeError`；用户输入/业务规则错误用自定义异常。

### 3.5 提交

```bash
git add exp_tracker/errors.py
git commit -m "feat: add custom error hierarchy"
```

---

## 4. `models.py`：`Experiment` 类

### 4.1 `__init__` 的四步

```python
def __init__(self, name, model, learning_rate, batch_size,
             accuracy, loss, notes="", experiment_id=None, created_at=None):
    # 1. 数值转换
    try:
        self.learning_rate = float(learning_rate)
        self.batch_size = int(batch_size)
        self.accuracy = float(accuracy)
        self.loss = float(loss)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"数值字段格式不正确: {exc}") from exc

    # 2. 字符串清洗
    self.name = str(name).strip() if name is not None else ""
    self.model = str(model).strip() if model is not None else ""
    self.notes = str(notes).strip() if notes is not None else ""

    # 3. ID 与时间
    self.experiment_id = str(experiment_id).strip() if experiment_id else uuid4().hex[:8]
    self.created_at = str(created_at).strip() if created_at else datetime.now().isoformat(timespec="seconds")

    # 4. 统一校验
    self.validate()
```

### 4.2 为什么要 `try/except` 包住数值转换

```python
Experiment(..., learning_rate="abc", ...)
```

`float("abc")` 会抛 `ValueError`。如果我们不包装，调用方会收到一个“语言层面”的 `ValueError`，而不是业务异常 `ValidationError`。包装后：

```python
raise ValidationError("数值字段格式不正确: could not convert string to float: 'abc'") from exc
```

调用方只需要捕获 `ValidationError`，同时 `__cause__` 还保留原始异常，方便调试。

### 4.3 `validate()` 的规则

```python
if not self.name:
    raise ValidationError("实验名 name 不能为空")
if len(self.name) > 50:
    raise ValidationError("实验名 name 不能超过 50 个字符")
if not self.model:
    raise ValidationError("模型名 model 不能为空")
if self.learning_rate <= 0:
    raise ValidationError("learning_rate 必须大于 0")
if self.batch_size <= 0:
    raise ValidationError("batch_size 必须大于 0")
if not 0 <= self.accuracy <= 1:
    raise ValidationError("accuracy 必须在 0 到 1 之间")
if self.loss < 0:
    raise ValidationError("loss 不能为负数")
if len(self.notes) > 500:
    raise ValidationError("notes 不能超过 500 个字符")
```

注意：

- `not self.name` 能同时处理 `""` 和 `"   "`（因为前面已经 `strip()`）。
- `0 <= self.accuracy <= 1` 是 Python 的链式比较，等价于 `0 <= x and x <= 1`。
- 不要用 `assert` 做业务校验：`python -O` 会移除 assert。

### 4.4 `to_dict()` 与 `from_dict()`

`to_dict()`：

```python
return {
    "experiment_id": self.experiment_id,
    "name": self.name,
    "model": self.model,
    "learning_rate": self.learning_rate,
    "batch_size": self.batch_size,
    "accuracy": self.accuracy,
    "loss": self.loss,
    "notes": self.notes,
    "created_at": self.created_at,
}
```

`from_dict()`：

```python
@classmethod
def from_dict(cls, data):
    if not isinstance(data, dict):
        raise ValidationError("实验记录必须是字典")

    required = ["name", "model", "learning_rate", "batch_size", "accuracy", "loss"]
    missing = [field for field in required if field not in data]
    if missing:
        raise ValidationError(f"实验记录缺少字段: {', '.join(missing)}")

    return cls(
        name=data["name"],
        model=data["model"],
        learning_rate=data["learning_rate"],
        batch_size=data["batch_size"],
        accuracy=data["accuracy"],
        loss=data["loss"],
        notes=data.get("notes", ""),
        experiment_id=data.get("experiment_id"),
        created_at=data.get("created_at"),
    )
```

设计点：

- 必填字段缺失时，一次性列出所有缺失项，而不是只报第一个。
- 可选字段用 `data.get(...)` 给默认值。
- 用 `@classmethod`，子类调用时 `cls` 会自动是子类。

### 4.5 `@property`、`__repr__`、`__eq__`

```python
@property
def is_successful(self):
    return self.accuracy >= 0.9
```

```python
def __repr__(self):
    return (
        f"Experiment(experiment_id={self.experiment_id!r}, "
        f"name={self.name!r}, model={self.model!r}, "
        f"learning_rate={self.learning_rate!r}, "
        f"batch_size={self.batch_size!r}, "
        f"accuracy={self.accuracy!r}, loss={self.loss!r})"
    )
```

```python
def __eq__(self, other):
    if not isinstance(other, Experiment):
        return NotImplemented
    return self.experiment_id == other.experiment_id
```

为什么 `__eq__` 按 ID：

- 同一条实验修改了 accuracy 后，仍然是同一条记录。
- 测试里 `assertEqual(exp, restored)` 更稳定。

### 4.6 常见错误

| 错误 | 后果 | 修正 |
|---|---|---|
| `self.accuracy = accuracy` 前没转 float | JSON 读回来可能是 int，比较/格式化不一致 | 统一 `float()` |
| `str(None)` 变成 `"None"` | 空名字校验失效 | 先判断 `is not None` |
| `from_dict` 只报第一个缺失字段 | 用户要反复试 | 一次性列出所有缺失 |
| `__eq__` 比较所有字段 | 改一个字段就不相等 | 按 ID 比较 |
| 用 `assert` 做校验 | `-O` 下失效 | 用 `raise` |

### 4.7 提交

```bash
git add exp_tracker/models.py
git commit -m "feat: implement Experiment model with validation"
```

---

## 5. `storage.py`：JSON 持久化

### 5.1 初始化：确保目录和文件存在

```python
def __init__(self, data_file):
    self.data_file = Path(data_file)
    self._ensure_storage()

def _ensure_storage(self):
    self.data_file.parent.mkdir(parents=True, exist_ok=True)
    if not self.data_file.exists():
        self._write_all([])
```

- `parents=True`：父目录不存在时逐级创建。
- `exist_ok=True`：目录已存在时不报错。
- 新文件写 `[]`，保证后续 `json.loads` 永远拿到 list。

### 5.2 读：`_read_all()`

```python
try:
    text = self.data_file.read_text(encoding="utf-8")
except OSError as exc:
    raise StorageError(f"读取数据文件失败: {self.data_file}") from exc

if not text.strip():
    return []

try:
    raw = json.loads(text)
except json.JSONDecodeError as exc:
    raise StorageError(f"数据文件不是合法 JSON: {self.data_file}") from exc

if not isinstance(raw, list):
    raise StorageError("数据文件的顶层必须是列表")

experiments = []
for index, item in enumerate(raw):
    if not isinstance(item, dict):
        raise StorageError(f"第 {index} 条记录不是 JSON 对象")
    try:
        experiments.append(Experiment.from_dict(item))
    except ValidationError as exc:
        raise StorageError(f"第 {index} 条记录校验失败: {exc}") from exc

return experiments
```

为什么要包装异常：

- `pathlib` 抛 `OSError`，`json` 抛 `JSONDecodeError`，`Experiment` 抛 `ValidationError`。
- 存储层把它们统一成 `StorageError`，上层只需要认识业务异常。
- `from exc` 保留原始异常链。

### 5.3 写：原子替换

```python
payload = [experiment.to_dict() for experiment in experiments]
tmp_file = self.data_file.with_name(self.data_file.name + ".tmp")

try:
    tmp_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_file.replace(self.data_file)
except OSError as exc:
    raise StorageError(f"写入数据文件失败: {self.data_file}") from exc
```

为什么不是直接 `write_text`：

```text
直接覆盖：打开正式文件 -> 写一半 -> 崩溃 -> 文件损坏
临时文件：写 .tmp -> 写完 -> replace -> 正式文件始终完整
```

`Path.replace` 在同一个文件系统内是原子操作。

### 5.4 增删查

```python
def add(self, experiment):
    if not isinstance(experiment, Experiment):
        raise TypeError("add() 只接受 Experiment 对象")
    experiments = self._read_all()
    if any(item.experiment_id == experiment.experiment_id for item in experiments):
        raise StorageError(f"实验 ID 已存在: {experiment.experiment_id}")
    experiments.append(experiment)
    self._write_all(experiments)
    return experiment
```

```python
def find_by_id(self, experiment_id):
    for experiment in self._read_all():
        if experiment.experiment_id == experiment_id:
            return experiment
    raise ExperimentNotFoundError(f"找不到实验: {experiment_id}")
```

```python
def delete(self, experiment_id):
    experiments = self._read_all()
    for index, experiment in enumerate(experiments):
        if experiment.experiment_id == experiment_id:
            deleted = experiments.pop(index)
            self._write_all(experiments)
            return deleted
    raise ExperimentNotFoundError(f"找不到实验: {experiment_id}")
```

设计点：

- `add` 先读后写；数据量小，简单可靠。
- 重复 ID 直接拒绝，避免“同 ID 两条记录”导致查找歧义。
- `delete` 返回被删对象，方便 CLI 显示/以后做撤销。

### 5.5 常见错误

| 错误 | 后果 | 修正 |
|---|---|---|
| 直接 `open(..., "w")` 覆盖 | 写一半崩溃会损坏文件 | 临时文件 + replace |
| 读空文件不判断 | `json.loads("")` 抛异常 | `if not text.strip(): return []` |
| 捕获 `Exception` 后不抛业务异常 | 上层不知道是存储问题 | 包装成 `StorageError` |
| `except` 后忘了 `from exc` | 丢失原始原因 | `raise ... from exc` |
| 用字符串拼路径 | 跨平台/可读性差 | `pathlib.Path` |

### 5.6 提交

```bash
git add exp_tracker/storage.py
git commit -m "feat: add JSON storage with atomic writes"
```

---

## 6. 手动 smoke test

在 `project/` 目录下执行：

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

python3 - <<'PY'
# 用临时目录，不污染 data/experiments.json
import tempfile
from pathlib import Path

from exp_tracker.errors import ExperimentNotFoundError
from exp_tracker.models import Experiment
from exp_tracker.storage import JsonExperimentStore

with tempfile.TemporaryDirectory() as tmp:
    data_file = Path(tmp) / "data" / "experiments.json"
    store = JsonExperimentStore(data_file)

    print("初始数量:", store.count())

    exp = Experiment(
        name="smoke-test",
        model="Qwen2.5-7B",
        learning_rate=1e-4,
        batch_size=8,
        accuracy=0.9,
        loss=0.2,
        notes="day4 smoke test",
    )
    store.add(exp)
    print("添加后:", store.count())
    print("查找到:", store.find_by_id(exp.experiment_id).summary())

    store.delete(exp.experiment_id)
    print("删除后:", store.count())

    try:
        store.find_by_id(exp.experiment_id)
    except ExperimentNotFoundError as exc:
        print("删除后再查，符合预期:", exc)
PY
```

预期输出：

```text
初始数量: 0
添加后: 1
查找到: [xxxxxxxx] smoke-test | model=Qwen2.5-7B | acc=0.900 | loss=0.200 | lr=0.0001 | bs=8
删除后: 0
删除后再查，符合预期: 找不到实验: xxxxxxxx
```

再跑模型/存储测试：

```bash
python3 -m unittest tests.test_models tests.test_storage -v
```

应该全绿。

---

## 7. 今日 Git 提交

至少 3 次：

```text
feat: add custom error hierarchy
feat: implement Experiment model with validation
feat: add JSON storage with atomic writes
```

检查：

```bash
git log --oneline
git status
```

---

## 8. 今日复盘

打开 `notes/2026-11-19.md`，在“待我填写的笔记”里写三行：

```text
今天产出：
今天卡点：
明天第一件事：
```

自查：

- [ ] 能解释四个异常各自的触发场景
- [ ] 能解释 `float()`/`int()` 转换失败时为什么要包装成 `ValidationError`
- [ ] 能解释 `to_dict` / `from_dict` 的字段契约
- [ ] 能解释原子写入解决什么问题
- [ ] smoke test 跑通
- [ ] 能独立写出四个异常，并在 storage 中正确包装底层错误

---

## 9. 明日预告

Day 5 写项目 part2：

- `service.py`：业务用例、汇总统计
- `cli.py` / `main.py`：菜单、输入校验、错误提示
- `tests/`：models/storage/service 全部测试
- 跑通 CLI，补 README，打 `v0.1.0` tag