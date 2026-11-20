# Day 5 · 项目 part2：service / cli / tests / README

> 阶段：S0 地基期 · W1 第 5 天
> 日期：2026-11-20（周五）
> 今日交付：项目可运行、测试全绿、README 可复现、打 `v0.1.0` tag

---

## 0. 今日路线

| 时间 | 内容 | 产出 |
|---|---|---|
| 0:00 - 0:10 | 回顾 part1：models/storage 的接口 | 口述一遍 |
| 0:10 - 0:50 | 实现 `service.py` | 业务用例 + 汇总统计 |
| 0:50 - 1:50 | 实现 `cli.py` / `main.py` | 菜单可交互 |
| 1:50 - 2:30 | 写 `tests/` | 三组测试全绿 |
| 2:30 - 2:50 | 跑 CLI，手工走一遍 | 新增/列表/查找/删除/汇总 |
| 2:50 - 3:00 | 补 README、提交、打 tag | `v0.1.0` |
| 3:00 - 4:00 | 补课 + 复盘 | 今日复盘 |

---

## 1. 回顾 part1 的接口

`models.py`：

```python
Experiment(name, model, learning_rate, batch_size, accuracy, loss,
           notes="", experiment_id=None, created_at=None)
experiment.to_dict()
Experiment.from_dict(data)
experiment.summary()
experiment.is_successful
```

`storage.py`：

```python
JsonExperimentStore(data_file)
store.add(experiment)
store.list_all()
store.find_by_id(experiment_id)
store.delete(experiment_id)
store.count()
```

`errors.py`：

```text
ExperimentTrackerError
├── ValidationError
├── StorageError
└── ExperimentNotFoundError
```

今天只在这些接口之上写业务和交互，不改 part1 的职责。

---

## 2. `service.py`：业务逻辑

### 2.1 为什么需要 service

CLI 不应该直接操作 storage：

- CLI 关心“怎么问、怎么显示”。
- storage 关心“怎么读写 JSON”。
- 业务规则（创建对象、汇总统计）放在 service。

以后加 Web API 时，可以直接复用 service。

### 2.2 组合 store

```python
class ExperimentService:
    def __init__(self, store):
        self.store = store
```

- 组合（has-a）：service 持有一个 store。
- 不在 service 里创建 `JsonExperimentStore`，方便测试时传入临时 store。
- service 只依赖 store 的 `add/list_all/find_by_id/delete` 方法（鸭子类型）。

### 2.3 添加实验

```python
def add_experiment(self, name, model, learning_rate, batch_size,
                   accuracy, loss, notes=""):
    experiment = Experiment(
        name=name,
        model=model,
        learning_rate=learning_rate,
        batch_size=batch_size,
        accuracy=accuracy,
        loss=loss,
        notes=notes,
    )
    return self.store.add(experiment)
```

- 构造函数负责校验；`ValidationError` 直接向上抛。
- service 不吞异常，让 CLI 统一处理。

### 2.4 列表、查找、删除

```python
def list_experiments(self):
    return self.store.list_all()

def find_experiment(self, experiment_id):
    return self.store.find_by_id(experiment_id)

def delete_experiment(self, experiment_id):
    return self.store.delete(experiment_id)
```

这些是“透传”，看起来多余；但保留 service 层是为了以后加权限、日志、缓存时不改 CLI。

### 2.5 汇总统计

```python
def summary(self):
    experiments = self.store.list_all()

    if not experiments:
        return {
            "count": 0,
            "best_accuracy": None,
            "best_experiment": None,
            "average_loss": None,
            "models": [],
        }

    best = max(experiments, key=lambda experiment: experiment.accuracy)
    average_loss = sum(experiment.loss for experiment in experiments) / len(experiments)
    models = sorted({experiment.model for experiment in experiments})

    return {
        "count": len(experiments),
        "best_accuracy": best.accuracy,
        "best_experiment": best.name,
        "average_loss": average_loss,
        "models": models,
    }
```

设计点：

- 返回字典而不是字符串：service 不管终端排版。
- 空数据返回稳定结构，调用方不用做 `None` 判断。
- `max(..., key=...)` 取准确率最高的实验。
- `{...}` 集合推导去重，`sorted` 保证输出稳定。

### 2.6 常见错误

| 错误 | 后果 | 修正 |
|---|---|---|
| 在 service 里直接 `open()` JSON | 绕过 storage，职责混乱 | 只调用 store 方法 |
| 空数据时返回 `None` | CLI 要到处判空 | 返回结构稳定的字典 |
| 在 service 里 `print()` | 业务层依赖终端 | 返回数据，由 CLI 打印 |
| 捕获 `ValidationError` 后返回 `None` | 调用方不知道失败 | 让异常向上抛 |

### 2.7 提交

```bash
# git add：把 service.py 加入暂存区
git add exp_tracker/service.py

# git commit：提交
# -m：提交说明
git commit -m "feat: add ExperimentService business logic"
```

---

## 3. `cli.py` / `main.py`：交互层

### 3.1 数据文件路径

```python
DEFAULT_DATA_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "experiments.json"
)
```

逐段解释：

```text
__file__        .../project/exp_tracker/cli.py
.resolve()      绝对路径
.parent         .../project/exp_tracker
.parent         .../project
/ "data"        .../project/data
/ "experiments.json"
```

好处：不管从哪个目录运行 `python3 main.py`，数据文件位置都固定。

### 3.2 输入辅助函数

```python
def _prompt_text(label, allow_empty=False):
    while True:
        value = input(label).strip()
        if value or allow_empty:
            return value
        print("输入不能为空，请重试。")

def _prompt_float(label):
    while True:
        text = input(label).strip()
        try:
            return float(text)
        except ValueError:
            print(f"请输入数字，收到: {text!r}")
```

设计点：

- 输入格式错误时循环重问，不退出整个程序。
- `allow_empty=True` 用于备注。
- 业务规则（accuracy 范围）不在这里校验，交给 `Experiment.validate()`。

### 3.3 菜单处理函数

```python
def _handle_add(service):
    print("\n== 新增实验 ==")
    name = _prompt_text("实验名: ")
    model = _prompt_text("模型名: ")
    learning_rate = _prompt_float("学习率（如 0.0001）: ")
    batch_size = _prompt_int("batch size: ")
    accuracy = _prompt_float("准确率（0~1）: ")
    loss = _prompt_float("loss: ")
    notes = _prompt_text("备注（可空）: ", allow_empty=True)

    experiment = service.add_experiment(
        name=name, model=model,
        learning_rate=learning_rate, batch_size=batch_size,
        accuracy=accuracy, loss=loss, notes=notes,
    )
    print("\n已添加：")
    _print_experiment(experiment)
```

注意：

- 这里不写 `try/except`；统一在 `run_cli()` 里捕获业务异常。
- `service.add_experiment` 校验失败会抛 `ValidationError`，由 `run_cli` 打印。

### 3.4 主循环

```python
def run_cli():
    store = JsonExperimentStore(DEFAULT_DATA_FILE)
    service = ExperimentService(store)

    actions = {
        "1": _handle_add,
        "2": _handle_list,
        "3": _handle_find,
        "4": _handle_delete,
        "5": _handle_summary,
    }

    while True:
        print(MENU)
        try:
            choice = input("请选择: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已退出。")
            break

        if choice == "0":
            print("再见。")
            break

        action = actions.get(choice)
        if action is None:
            print("无效选择，请输入 0-5。")
            continue

        try:
            action(service)
        except ExperimentTrackerError as exc:
            print(f"\n操作失败: {exc}")
        except (KeyboardInterrupt, EOFError):
            print("\n已取消当前操作。")
```

设计点：

- 只捕获 `ExperimentTrackerError`：业务错误打印友好提示；其他异常让它暴露，方便发现 bug。
- `KeyboardInterrupt` / `EOFError` 在输入时取消当前操作或退出。
- `actions` 字典把菜单编号映射到函数，避免长串 `if/elif`。

### 3.5 `main.py`

```python
from exp_tracker.cli import run_cli

if __name__ == "__main__":
    run_cli()
```

入口只做启动，不写业务逻辑。

### 3.6 提交

```bash
# git add：把两个文件加入暂存区
# 多个文件名用空格分隔
git add exp_tracker/cli.py main.py

# git commit：提交
# -m：提交说明
git commit -m "feat: add interactive CLI"
```

---

## 4. `tests/`：单元测试

### 4.1 为什么用 `unittest`

- 标准库自带，2C2G 不用装 pytest。
- W2 会引入 pytest；先理解 `TestCase`、`assertEqual`、`assertRaises`、`setUp/tearDown`。
- 测试是“可复现交付物”的一部分：面试时你可以说“我有测试覆盖边界”。

### 4.2 测试结构

```text
tests/
├── __init__.py
├── test_models.py      # 校验、序列化、相等性
├── test_storage.py     # 临时目录、增删查、损坏 JSON、持久化
└── test_service.py     # 业务、汇总、校验传播
```

### 4.3 测试重点

`test_models.py`：

- 合法数据能创建
- accuracy 越界、学习率为 0、空名字 → `ValidationError`
- `to_dict` / `from_dict` 往返一致
- `__eq__` 按 ID 比较
- `repr` 包含 ID

`test_storage.py`：

- 初始化自动建目录和空文件
- add/list/find/delete
- 找不到 ID → `ExperimentNotFoundError`
- 重复 ID → `StorageError`
- 损坏 JSON → `StorageError`
- 顶层不是列表 → `StorageError`
- 新建 store 能读到之前的数据

`test_service.py`：

- 空数据 summary 结构稳定
- add/list
- summary 的最高准确率、平均 loss、模型排序
- find/delete
- 校验失败时存储不留下记录

### 4.4 临时目录

```python
def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.data_file = Path(self.temp_dir.name) / "data" / "experiments.json"
    self.store = JsonExperimentStore(self.data_file)

def tearDown(self):
    self.temp_dir.cleanup()
```

好处：

- 每个测试独立，不污染 `data/experiments.json`。
- 测试结束自动删除临时目录。
- 故意多一层 `data/`，顺便测试“父目录自动创建”。

### 4.5 运行

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# 全部测试
# python3 -m：运行标准库模块（-m = module）
# unittest：测试框架
# discover：自动发现测试
# -s tests：start directory，从 tests/ 开始找 test_*.py
# -v：verbose，输出每个用例名称和结果
python3 -m unittest discover -s tests -v

# 单个文件
# tests.test_models：模块路径；-v：verbose
python3 -m unittest tests.test_models -v
```

预期：

```text
Ran 23 tests in 0.0XXs

OK
```

### 4.6 常见错误

| 现象 | 原因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: exp_tracker` | 不在 `project/` 下运行 | `cd project` |
| 测试互相影响 | 共用了 `data/experiments.json` | 用 `TemporaryDirectory` |
| `AssertionError` 在 summary | 平均 loss 算法错/模型没排序 | 检查 `sum/len` 和 `sorted` |
| 测试通过但 CLI 报错 | CLI 输入解析/路径问题 | 单独跑 CLI 手工验证 |

### 4.7 提交

```bash
git add tests/
git commit -m "test: add unit tests for models/storage/service"
```

---

## 5. 手工走一遍 CLI

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project
python3 main.py
```

按顺序操作：

1. 输入 `2`：应看到 `data/experiments.json` 里的两条示例数据。
2. 输入 `5`：看到总数 2、最高准确率 0.923、平均 loss 0.2200、两个模型。
3. 输入 `1`：新增一条：
   ```text
   实验名: test-run
   模型名: Qwen2.5-7B
   学习率: 0.0001
   batch size: 8
   准确率: 0.88
   loss: 0.3
   备注: manual test
   ```
4. 输入 `2`：应看到 3 条。
5. 记录新实验的 ID（8 位十六进制）。
6. 输入 `3`，输入 ID：应找到它。
7. 输入 `4`，输入 ID，确认 `y`：应删除。
8. 输入 `0`：退出。

再测错误路径：

- 新增时 `准确率: 1.5` → 应提示“accuracy 必须在 0 到 1 之间”，并且不写入。
- 查找不存在的 ID → 应提示“找不到实验”。
- 输入 `abc` 当学习率 → 应提示“请输入数字”，并重新询问。

非交互式快速验证：

```bash
# printf：按格式输出字符串
# '2\n5\n0\n'：依次输出 2、换行、5、换行、0、换行
#   \n 是换行符
# |：管道，把 printf 的输出作为 python3 的标准输入
# python3 main.py：运行菜单程序，自动依次选择 2、5、0
printf '2\n5\n0\n' | python3 main.py
```

---

## 6. README 与收尾

项目 README 至少包含：

- 项目做什么
- 架构图 / 依赖方向
- 文件职责
- 运行方式（直接运行 + venv）
- 测试方式
- 数据格式
- 设计说明（为什么分层、为什么原子写、为什么按 ID 比较）
- W2 重构预告
- 常见问题

检查：

```bash
git status
git diff
```

提交：

```bash
# git add：把多个文件加入暂存区
# 文件名之间用空格分隔
git add README.md requirements.txt .gitignore data/experiments.json

# git commit：提交
# -m：提交说明
git commit -m "docs: add project README and sample data"
```

打 tag：

```bash
# git tag：管理标签
# -a：annotated，创建带说明的附注标签
# v0.1.0：标签名
# -m：标签说明
git tag -a v0.1.0 -m "W1 experiment tracker v0.1.0"

# git log：查看历史
# --oneline：一行一个提交
# --decorate：显示分支、标签等引用指向
git log --oneline --decorate
```

---

## 7. 今日复盘

打开 `notes/2026-11-20.md`，在“待我填写的笔记”里写三行：

```text
今天产出：
今天卡点：
明天第一件事：
```

自查：

- [ ] 全部 23 个测试通过
- [ ] CLI 能新增、列表、查找、删除、汇总
- [ ] 非法 accuracy 被拒绝，且没有写入
- [ ] 数据文件路径不随运行目录变化
- [ ] 已打 `v0.1.0` tag
- [ ] 能解释 service 与 cli 的职责边界

---

## 8. 明日预告

Day 6 是补漏日：

- 按重构清单逐项检查
- 补边界测试
- 按 W1 出口标准自测
- 写周复盘初稿

不新增功能，只把已有代码变干净、变可靠。

---

## 9. 复盘问答

> 这些问题来自 service、CLI、测试和收尾。重点回答“为什么要分层”“测试怎么信得过”。

### Q1. `service` 很多方法只是透传，为什么还要这一层？什么时候可以删掉？

W1 的 `service` 确实很薄：

```python
def list_experiments(self):
    return self.store.list_all()
```

但它是一个**边界**，以后会长出：

- 权限检查（谁能删）
- 操作日志（谁在什么时候删了什么）
- 缓存（避免每次读 JSON）
- 事务/批量导入
- 指标统计

如果 CLI 直接调 storage，这些逻辑要么塞进 CLI，要么塞进 storage，最后两侧都变脏。

什么时候可以删：

- 真正的一次性脚本，没有复用/扩展计划。
- 项目小到“service 永远只是透传”，且你接受以后重构。

工程判断：**为当前需求设计，但给变化留接缝**。W1 的接缝就是 service 层；它很薄，但方向是对的。

### Q2. `cli` 为什么只捕获 `ExperimentTrackerError`？其他异常怎么办？

```python
try:
    action(service)
except ExperimentTrackerError as exc:
    # 业务异常：打印友好提示，不打印 traceback
    print(f"操作失败: {exc}")
```

- `ExperimentTrackerError` 是“用户能理解、能处理”的错误：输入不合法、找不到记录、JSON 损坏。
- 其他异常（`TypeError`、`AttributeError`、`KeyError`）通常是**程序 bug**，不应该被伪装成“操作失败”。让它们抛出 traceback，你才能定位。
- 如果这是生产服务，最外层可以捕获所有异常并记录日志，但**不能吞掉**；至少要记录完整 traceback 并返回 500。

W1 是学习项目，选择“业务异常友好提示，程序异常直接暴露”，这是故意的。

### Q3. 为什么用 `unittest` 而不是 pytest？W2 换 pytest 要注意什么？

W1 用 `unittest` 的原因：

- 标准库自带，2C2G 不用装依赖。
- 让你理解 `TestCase`、`setUp/tearDown`、`assertRaises` 这些基本概念。
- 面试可能问“你怎么写测试”，标准库足够表达。

pytest 的优势：

- 断言直接写 `assert`，不用 `self.assertEqual`。
- fixture、参数化、插件生态更好。
- 更适合大型项目。

W2 迁移时：

- 测试文件命名仍是 `test_*.py`。
- `unittest` 的测试可以被 pytest 直接运行，通常不用重写。
- 逐步把 `self.assertX` 改成 `assert`，把 `setUp` 改成 fixture。

不要为了“工具更高级”在 W1 引入 pytest；先把测试思维练出来。

### Q4. 测试为什么要用临时目录？不用会怎样？

如果测试直接用 `project/data/experiments.json`：

- 测试会污染你的真实数据。
- 测试之间互相影响，顺序变了结果就变。
- 并行跑测试会互相覆盖。
- 失败后残留数据，下一次测试可能“假通过”。

临时目录保证隔离：

```python
def setUp(self):
    # TemporaryDirectory：创建临时目录，tearDown 时递归删除
    self.temp_dir = tempfile.TemporaryDirectory()
    # 每个测试用独立文件
    self.data_file = Path(self.temp_dir.name) / "experiments.json"
    self.store = JsonExperimentStore(self.data_file)

def tearDown(self):
    # cleanup：删除临时目录
    self.temp_dir.cleanup()
```

工程原则：**测试不应该依赖外部状态，也不应该留下外部状态**。

### Q5. 测试全绿，但 CLI 仍然报错，怎么排查？

测试覆盖的是 models/storage/service，CLI 还多了：

- `input()` 解析
- 菜单分支
- 数据文件路径
- 异常捕获/打印

分层排查：

```bash
# 1. 先确认测试本身全绿
# -m：运行模块；unittest：测试框架
# discover：自动发现；-s tests：从 tests/ 开始；-v：verbose
python3 -m unittest discover -s tests -v

# 2. 直接调用 service，绕过 CLI
# -c：直接执行一段 Python 代码
python3 -c "from exp_tracker.cli import DEFAULT_DATA_FILE; print(DEFAULT_DATA_FILE)"

# 3. 用管道喂输入，复现 CLI 路径
# printf 输出 2、5、0；| 把输出作为 main.py 的标准输入
printf '2\n5\n0\n' | python3 main.py
```

常见原因：

- `DEFAULT_DATA_FILE` 指向了别处（打印路径确认）。
- 输入不是数字/范围不对，触发 `ValidationError`。
- 数据文件被手动改坏，JSON 解析失败。

工程习惯：**单元测试保证逻辑，集成测试/手工冒烟保证入口**；两者都要有。

### Q6. `DEFAULT_DATA_FILE` 为什么用 `__file__` 计算？用 `Path("data/experiments.json")` 会怎样？

`Path("data/experiments.json")` 是**相对当前工作目录**的路径：

- 在 `project/` 下运行，能找到 `project/data/...`。
- 在 `/root/aiinfra` 下运行，会找 `/root/aiinfra/data/...`，找不到或写错地方。

`__file__` 计算的是“代码文件自己的位置”，与当前工作目录无关：

```python
# __file__：当前文件路径 .../project/exp_tracker/cli.py
# .resolve()：转绝对路径
# .parent：.../project/exp_tracker
# .parent：.../project
DEFAULT_DATA_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "experiments.json"
)
```

工程原则：**程序内部引用的资源，用相对于代码文件的路径；用户传入的路径，才用相对于当前目录的路径**。

### Q7. `git tag -a` 和轻量标签有什么区别？tag 要不要推？

- 轻量标签：`git tag v0.1.0`，只是一个指向 commit 的引用。
- 附注标签：`git tag -a v0.1.0 -m "..."`，带作者、日期、说明，推荐用于版本发布。

```bash
# -a：annotated，创建附注标签
# -m：标签说明
git tag -a v0.1.0 -m "W1 experiment tracker v0.1.0"

# 普通 git push 不会推送标签
# origin：远程名；v0.1.0：标签名
git push origin v0.1.0

# 或一次推送所有标签
# --tags：推送所有本地标签
git push --tags
```

什么时候打 tag：

- 一个可交付版本完成（W1 项目 v0.1.0）。
- 压测报告/简历项目对应的代码状态。
- 不要在每次 commit 都打 tag；tag 是里程碑，不是提交记录。

团队协作时，tag 命名建议用语义化版本：`v0.1.0`、`v0.2.0`、`v1.0.0`。

### Q8. 测试文件里写 `from ..exp_tracker.errors import ...` 为什么报 `ImportError`？测试应该怎么导入项目代码？

现象：

```text
ImportError: attempted relative import with no known parent package
```

原因：相对导入 `..` 需要“包上下文”。在 `project/` 目录下运行：

```bash
# -m：运行模块；unittest：测试框架
# discover：自动发现测试；-s tests：从 tests/ 目录开始
# -v：verbose，输出每个用例
python3 -m unittest discover -s tests -v
```

此时 `tests/test_models.py` 被当作顶层模块（或顶层包 `tests`）加载，`..` 想找 `tests` 的父包，但 `project/` 本身不是包，所以失败。

W1 推荐写法：**绝对导入**。

```python
# 从 project/ 运行时，project/ 在 sys.path 里
# 所以可以直接导入 exp_tracker 包
from exp_tracker.errors import ValidationError
from exp_tracker.models import Experiment
```

如果你一定要用相对导入，需要让 `project` 成为包，并换一种发现方式：

```bash
# 在 W1 目录（project 的上一级）运行
# -s project/tests：从 project/tests 开始发现
# -t .：top-level directory 设为当前目录
# 这样模块名是 project.tests.test_models，.. 才能指向 project
python3 -m unittest discover -s project/tests -t . -v
```

但这要求 `project/__init__.py` 存在，而且会让项目结构更绕。W1 不推荐；测试统一用绝对导入，和 README 里的运行方式保持一致。

工程原则：**测试的导入方式要和项目的运行方式一致**。项目从 `project/` 根目录运行，测试也从这里运行，使用绝对导入最稳。
