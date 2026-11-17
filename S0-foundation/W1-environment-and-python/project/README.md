# 实验记录器（Experiment Tracker）

> S0 · W1 主项目
> 目标：用“类、模块、异常、JSON、Git”做一个能运行、能测试、能讲清的小工程。
> 依赖：**只用 Python 标准库**，2C2G 服务器可直接跑。

---

## 1. 它做什么

一个命令行小工具，记录模型训练/评测实验：

- 新增实验：名字、模型、学习率、batch size、准确率、loss、备注
- 查看全部实验
- 按 ID 查找
- 按 ID 删除
- 汇总统计：总数、最高准确率、平均 loss、涉及的模型
- 数据持久化到 `data/experiments.json`

它不做什么：

- 不训练模型
- 不连数据库
- 不做 Web 服务
- 不依赖 PyTorch

W1 的重点是“工程结构”，不是功能数量。

---

## 2. 架构

```text
main.py
   │  启动
   ▼
exp_tracker/cli.py          菜单、输入、输出、错误提示
   │  调用
   ▼
exp_tracker/service.py      业务用例：添加、列表、查找、删除、汇总
   │  调用
   ▼
exp_tracker/storage.py      JSON 读写、原子替换、查找、删除
   │  创建/读取
   ▼
exp_tracker/models.py       Experiment：字段、校验、序列化
   │
   └── exp_tracker/errors.py   自定义异常（所有层共用）
```

依赖方向是单向的：

```text
cli → service → storage → models
                         ↘ errors ↙
```

- `models.py` 不导入 `storage/service/cli`
- `storage.py` 不导入 `service/cli`
- `errors.py` 是叶子模块，谁都可以导入

---

## 3. 文件职责

| 文件 | 职责 | 不该做的事 |
|---|---|---|
| `main.py` | 程序入口，调用 `run_cli()` | 写业务逻辑 |
| `exp_tracker/errors.py` | 定义异常层级 | 读写文件 |
| `exp_tracker/models.py` | `Experiment` 数据、校验、`to_dict/from_dict` | 读写 JSON、打印菜单 |
| `exp_tracker/storage.py` | JSON 文件读写、查找、删除 | 业务汇总、用户输入 |
| `exp_tracker/service.py` | 业务用例、汇总统计 | 直接读写文件、打印 |
| `exp_tracker/cli.py` | 菜单、输入、输出、错误提示 | 业务规则、JSON 细节 |
| `exp_tracker/__init__.py` | 对外暴露包 API | 写业务逻辑 |
| `tests/` | 单元测试 | 依赖真实用户输入 |

---

## 4. 运行

### 4.1 直接运行（W1 先不用虚拟环境）

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# 启动菜单
python3 main.py
```

你会看到：

```text
数据文件: /root/aiinfra/S0-foundation/W1-environment-and-python/project/data/experiments.json

================ 实验记录器 ================
1. 新增实验
2. 查看全部
3. 按 ID 查找
4. 按 ID 删除
5. 汇总统计
0. 退出
============================================

请选择:
```

### 4.2 用虚拟环境运行（练习 venv）

虽然本项目只用标准库，但 W1 要求掌握虚拟环境。建议从今天开始在项目里用 `.venv`：

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# 创建虚拟环境
# python3 -m：把后面的模块当脚本运行（-m = module）
# venv：Python 标准库的虚拟环境模块
# .venv：虚拟环境目录名（约定用 .venv，已在 .gitignore 里）
python3 -m venv .venv

# 激活虚拟环境
# source：在当前 shell 中执行脚本（不是开子进程）
# .venv/bin/activate：激活脚本路径
# 激活后命令行前面会出现 (.venv)
source .venv/bin/activate

# 确认用的是虚拟环境里的 python
# which：在 PATH 里查找可执行文件的位置
which python

# --version：打印 Python 版本
python --version

# 升级 pip（可选）
# python -m pip：用当前 Python 的 pip 模块
# install --upgrade pip：安装并升级 pip 本身
python -m pip install --upgrade pip

# 运行
python main.py

# 退出虚拟环境
# deactivate：撤销 activate 设置的环境变量
deactivate
```

`.venv/` 已经在 `.gitignore` 里，不会被提交。

### 4.3 跑测试

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# 发现 tests/ 下所有 test_*.py 并运行
# python3 -m：运行模块（-m = module）
# unittest：标准库测试框架
# discover：自动发现测试
# -s tests：start directory，从 tests/ 开始
# -v：verbose，输出每个用例
python3 -m unittest discover -s tests -v
```

预期：

```text
test_add_and_list (tests.test_service.TestExperimentService) ... ok
...
----------------------------------------------------------------------
Ran 17 tests in 0.0XXs

OK
```

如果某个测试失败，先读失败信息里的 `AssertionError`，再回到对应模块检查。

### 4.4 非交互式快速验证

不想走菜单时，可以直接用 Python 一行验证：

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# python3：调用解释器
# -：从标准输入读取脚本（不是从文件）
# <<'PY'：here-document，直到单独一行 PY；引号表示不做变量替换
python3 - <<'PY'
# 用临时文件，不污染 data/experiments.json
import tempfile
from pathlib import Path
from exp_tracker import ExperimentService, JsonExperimentStore

with tempfile.TemporaryDirectory() as tmp:
    store = JsonExperimentStore(Path(tmp) / "experiments.json")
    service = ExperimentService(store)

    exp = service.add_experiment(
        name="smoke-test",
        model="Qwen2.5-7B",
        learning_rate=1e-4,
        batch_size=8,
        accuracy=0.9,
        loss=0.2,
    )
    print("created:", exp.summary())
    print("count:", len(service.list_experiments()))
    print("summary:", service.summary())
PY
```

---

## 5. 数据格式

`data/experiments.json` 是一个数组：

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
    "notes": "S0 示例数据：单卡 4090，3 个 epoch。",
    "created_at": "2026-11-16T09:00:00"
  }
]
```

字段规则：

| 字段 | 类型 | 规则 |
|---|---|---|
| `experiment_id` | string | 唯一；不传时自动生成 8 位十六进制 |
| `name` | string | 非空，≤ 50 字符 |
| `model` | string | 非空 |
| `learning_rate` | float | > 0 |
| `batch_size` | int | > 0 |
| `accuracy` | float | 0 ≤ x ≤ 1 |
| `loss` | float | ≥ 0 |
| `notes` | string | 可空，≤ 500 字符 |
| `created_at` | string | ISO 8601 时间字符串 |

---

## 6. 设计说明

### 6.1 为什么分这么多层

如果所有代码都写在 `main.py`：

- 想测试“校验逻辑”，必须启动菜单、手动输入。
- 想换存储方式，要改遍所有地方。
- 想加 Web API，业务逻辑无法复用。

分层后：

- `models` 可以单独测试校验。
- `storage` 可以用临时目录测试读写。
- `service` 可以用假 store 测试业务。
- `cli` 只负责交互，改菜单不影响业务。

### 6.2 为什么用自定义异常

`ValidationError` / `StorageError` / `ExperimentNotFoundError` 让调用方可以：

- 只捕获业务异常：`except ExperimentTrackerError`
- 区分“输入错了”和“文件坏了”
- 在错误信息里写清楚“哪条记录、哪个字段”

### 6.3 为什么 JSON 写入要“临时文件 + replace”

直接覆盖写：

```text
打开正式文件 -> 写一半 -> 进程崩溃 -> 文件损坏
```

临时文件 + 原子替换：

```text
写 experiments.json.tmp -> 写完 -> replace 成 experiments.json
```

任何时刻，正式文件要么是旧的完整版本，要么是新的完整版本。

### 6.4 为什么 `__eq__` 按 ID 比较

同一条实验修改了 accuracy 后，仍然是同一条记录。按 ID 比较符合业务语义，也让测试稳定。

---

## 7. W2 会怎么重构

W2 会在这个项目上继续改，不会换项目：

1. `Experiment` 改成 `@dataclass`，减少样板代码。
2. 加类型标注（`str`、`float`、`list[Experiment]`）。
3. 加 `logging`，替换部分 `print`，记录操作日志。
4. 用 `argparse` 把菜单改成子命令：

   ```bash
   python main.py add --name ... --model ...
   python main.py list
   python main.py summary
   ```

5. 用装饰器给 service 方法加计时/日志。
6. 用上下文管理器管理文件写入/临时目录。
7. 用迭代器/生成器处理大量记录（不一次性读入内存）。
8. 把 `requirements.txt` 和虚拟环境流程补完整。

所以 W1 的代码不是“写完就扔”，而是 W2 重构的基线。

---

## 8. 练习题（先自己写，再看答案）

### 练习 1：增加 `update` 功能

需求：

- `JsonExperimentStore.update(experiment)`：按 ID 找到并替换，找不到抛 `ExperimentNotFoundError`。
- `ExperimentService.update_experiment(experiment_id, **changes)`：只允许改 `notes`、`accuracy`、`loss`。
- CLI 加菜单 6：按 ID 修改备注/准确率/loss。

提示：

- 修改后要重新 `validate()`。
- 不要直接改文件里的字典；先读成对象，改对象，再整体写回。

### 练习 2：按模型筛选

需求：

- `ExperimentService.filter_by_model(model)`：返回该模型的所有实验。
- CLI 加菜单 7。

提示：

- 可以用列表推导式。
- 注意大小写：`Qwen2.5-7B` 和 `qwen2.5-7b` 是否算同一个？先定规则再写。

### 练习 3：导出 CSV

需求：

- `ExperimentService.export_csv(path)`：把所有实验写成 CSV。
- 用标准库 `csv`，不要装 pandas。

提示：

- `csv.DictWriter` 可以直接写字典。
- 注意 `encoding="utf-8"` 和 `newline=""`。

### 练习 4：更严格的 ID 校验

需求：

- `experiment_id` 只能是 8 位十六进制字符。
- 不合法时抛 `ValidationError`。

提示：

- 字符串方法 `all(c in "0123456789abcdef" for c in value)`。
- 注意大小写是否统一。

### 练习 5：给汇总加“按模型分组”

需求：

- `summary()` 返回 `by_model`：每个模型的实验数、最高准确率、平均 loss。

提示：

- 用字典累积：`{model: {"count": ..., "best": ..., "loss_sum": ...}}`。
- 最后再算平均，避免边加边除。

---

## 9. 常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: No module named 'exp_tracker'` | 不在 `project/` 目录下运行，或 `sys.path` 不对 | `cd project` 后 `python3 main.py` |
| `json.decoder.JSONDecodeError` | 手动改坏了 `data/experiments.json` | 用 JSON 校验器检查；或删掉文件让它重新生成 |
| `ValidationError: accuracy 必须在 0 到 1 之间` | 输入了 92.3 而不是 0.923 | 输入比例，不是百分数 |
| `StorageError: 实验 ID 已存在` | 从 JSON 导入时 ID 冲突 | 换一个 ID，或先删除旧记录 |
| 菜单里 Ctrl+C 没退出 | 代码只取消了当前操作 | 再按一次 0 退出；或 Ctrl+D |
| 测试找不到 | 没在 `project/` 下运行 | `cd project` 后执行 `python3 -m unittest discover -s tests -v` |

---

## 10. Git 提交建议

每完成一个文件/一个里程碑提交一次：

```text
feat: add custom error hierarchy
feat: implement Experiment model with validation
feat: add JSON storage with atomic writes
feat: add ExperimentService business logic
feat: add interactive CLI
test: add unit tests for models/storage/service
docs: add project README
chore: add sample data and gitignore
```

W1 结束时：

```bash
# git tag：管理标签
# -a：annotated，创建带说明的附注标签
# v0.1.0：标签名
# -m：标签说明
git tag -a v0.1.0 -m "W1 experiment tracker v0.1.0"
```
