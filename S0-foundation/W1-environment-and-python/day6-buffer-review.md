# Day 6 · 补漏、重构、W1 自测

> 阶段：S0 地基期 · W1 第 6 天
> 日期：2026-11-21（周六）
> 今日交付：干净的代码 + 补全的边界测试 + W1 自测表 + 周复盘初稿

> 今天不新增功能。只做三件事：修、测、讲清。

---

## 0. 今日路线

| 时间 | 内容 | 产出 |
|---|---|---|
| 0:00 - 0:20 | 跑全部测试 + 手工 CLI 回归 | 确认基线 |
| 0:20 - 1:20 | 按重构清单逐项检查并修改 | 更干净的代码 |
| 1:20 - 2:10 | 补边界测试（至少 5 个新用例） | 测试更全 |
| 2:10 - 2:40 | 按 W1 出口标准自测 | 自测表 |
| 2:40 - 3:00 | 补 README / 复盘 / 提交 | 可讲清的仓库 |
| 3:00 - 4:00 | 写周复盘初稿 | `notes/2026-11-21.md` 笔记区 |

---

## 1. 先跑基线

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python/project

# 全部测试
# python3 -m：运行标准库模块（-m = module）
# unittest：测试框架
# discover：自动发现测试
# -s tests：start directory，从 tests/ 开始
# -v：verbose，输出每个用例
python3 -m unittest discover -s tests -v

# 语法检查
# python3 -m compileall：递归编译 .py 检查语法
# -q：quiet，只输出错误
python3 -m compileall -q exp_tracker main.py

# 非交互 CLI 冒烟
# printf：输出 2、5、0 三个菜单选择（\n 是换行）
# |：管道，把输出作为 python3 的标准输入
# tail -20：只显示最后 20 行（-20 = 最后 20 行；-n 20 的简写）
printf '2\n5\n0\n' | python3 main.py | tail -20

# Git 状态
git status

# --oneline：一行一个提交
# --decorate：显示分支/标签引用
git log --oneline --decorate
```

如果测试没全绿，先修测试，不要开始重构。

---

## 2. 重构清单

逐项检查，每项问自己“为什么”：

### 2.1 命名

- [ ] 变量名能看出含义：`experiments` 而不是 `data`，`experiment_id` 而不是 `id`。
- [ ] 函数名是动词：`add_experiment`、`find_by_id`、`_read_all`。
- [ ] 私有方法/内部属性用 `_` 开头：`_read_all`、`_write_all`、`_accuracy`。
- [ ] 没有无意义的缩写：`cfg` 可以，`x1` 不行。

### 2.2 职责

- [ ] `models.py` 没有 `open()` / `json` / `print()`。
- [ ] `storage.py` 没有 `input()` / `print()` / 业务汇总。
- [ ] `service.py` 没有直接读写文件。
- [ ] `cli.py` 没有 `json.load` / 文件路径拼接。
- [ ] `main.py` 只有入口。

### 2.3 异常

- [ ] 业务错误用 `ExperimentTrackerError` 子类。
- [ ] 捕获底层异常后，用 `raise ... from exc` 保留原因。
- [ ] 没有裸 `except:`。
- [ ] 没有“捕获后静默 pass”。
- [ ] CLI 只捕获业务异常 + 用户中断；其他异常让它暴露。
- [ ] 校验失败时不会部分写入。

### 2.4 数据一致性

- [ ] `to_dict` 和 `from_dict` 字段一一对应。
- [ ] `from_dict` 缺字段时一次性列出所有缺失项。
- [ ] 数值字段统一 `float` / `int`。
- [ ] 空字符串/空白字符串被拒绝。
- [ ] ID 唯一。
- [ ] 写入是原子的（临时文件 + replace）。

### 2.5 注释

- [ ] 注释解释“为什么”，不是重复“做什么”。
- [ ] 每个模块顶部有职责说明。
- [ ] 每个公开函数/类有 docstring。
- [ ] 复杂分支/边界有注释。
- [ ] 没有过时注释（改了代码没改注释）。

### 2.6 测试

- [ ] 正常路径有测试。
- [ ] 空数据有测试。
- [ ] 非法输入有测试。
- [ ] 文件损坏有测试。
- [ ] 找不到 ID 有测试。
- [ ] 重复 ID 有测试。
- [ ] 测试用临时目录，不污染真实数据。
- [ ] 测试不依赖执行顺序。

### 2.7 可复现

- [ ] README 的命令能直接复制运行。
- [ ] `data/experiments.json` 是合法 JSON。
- [ ] `requirements.txt` 说明了“W1 无第三方依赖”。
- [ ] `.gitignore` 覆盖 `.venv/`、`__pycache__/`、`*.tmp`。
- [ ] 没有提交密钥/密码/大文件。

---

## 3. 补 5 个边界测试

自己写，不要只抄。建议从下面选 5 个：

1. **空名字**：`name="   "` → `ValidationError`
2. **accuracy 边界**：`0` 和 `1` 合法；`-0.1`、`1.1` 非法
3. **batch_size 为 0 或负数** → `ValidationError`
4. **notes 超长**（501 字符）→ `ValidationError`
5. **from_dict 缺少多个字段**：错误信息里同时包含缺失字段名
6. **JSON 顶层是对象** → `StorageError`
7. **JSON 某条记录不是对象** → `StorageError`
8. **删除后再次删除** → `ExperimentNotFoundError`
9. **两个 store 指向同一文件**：一个写入，另一个能读到
10. **summary 对全负数 loss？**（loss 不允许负数，测非法）
11. **summary 平均 loss 精度**：用 `assertAlmostEqual`
12. **CLI 路径**：`DEFAULT_DATA_FILE` 是否指向 `project/data/experiments.json`

示例（test_models.py 里加）：

```python
def test_accuracy_boundaries(self):
    """0 和 1 是合法边界，越界才报错。"""
    for value in (0, 1):
        exp = make_experiment(accuracy=value)
        self.assertEqual(exp.accuracy, float(value))

    for value in (-0.1, 1.1):
        with self.assertRaises(ValidationError):
            make_experiment(accuracy=value)
```

示例（test_storage.py 里加）：

```python
def test_record_must_be_object(self):
    """数组里某条不是对象时，报 StorageError。"""
    self.data_file.write_text(json.dumps([1, 2]), encoding="utf-8")

    with self.assertRaises(StorageError):
        self.store.list_all()
```

跑：

```bash
# -m：运行模块；unittest：测试框架
# discover：自动发现；-s tests：从 tests/ 开始
# -v：verbose，输出每个用例
python3 -m unittest discover -s tests -v
```

目标：至少 28 个测试全绿。

---

## 4. W1 出口标准自测

逐项打勾，并在旁边写“证据”：

- [ ] 能不看教程，独立写出一个带类、模块拆分、异常处理的 Python 小项目
  - 证据：
- [ ] 能解释 `__init__`、`self`、实例属性、类属性、继承、组合
  - 证据：
- [ ] 能解释模块、包、`__name__ == "__main__"`、绝对导入与相对导入
  - 证据：
- [ ] 能解释 `try/except/else/finally`、自定义异常、`raise ... from ...`
  - 证据：
- [ ] 在服务器上独立完成 Git 提交、分支、合并、回滚
  - 证据：
- [ ] SSH 免密可用；tmux 断开重连后任务还在
  - 证据：
  - 证据：

> “证据”可以是一个文件名、一条测试输出、一个 commit hash、一段你自己写的解释。没有证据就是没掌握。

---

## 5. 口述练习（10 分钟）

找一张纸，不看代码，写出：

1. `Experiment.__init__` 的四步。
2. `to_dict` / `from_dict` 的字段契约。
3. `storage._write_all` 的原子写入流程。
4. `cli → service → storage → models` 的依赖方向。
5. 三个自定义异常和它们的触发场景。

写完对照代码，把漏掉的补进复盘。

---

## 6. 补 README / 提交

如果 README 还缺：

- 运行方式
- 测试方式
- 架构图
- 数据格式
- 常见问题

补完后：

```bash
# git add：加入暂存区
# .：当前目录及子目录
git add .

# git commit：提交
# -m：提交说明
git commit -m "refactor: clean up W1 project and add edge-case tests"

# git log：查看历史
# --oneline：一行一个提交
# --decorate：显示分支/标签引用
git log --oneline --decorate
```

如果改了功能（不只是测试），提交信息写清：

```text
fix: ...
refactor: ...
test: ...
docs: ...
```

---

## 7. 写周复盘初稿

打开 `notes/2026-11-21.md`，在“待我填写的笔记”里写四行：

```text
本周完成：
没达标：
最大卡点：
W2 第一件事：
```

周日再补一次，不要拖到下周。

---

## 8. 今日复盘

打开 `notes/2026-11-21.md`，在“待我填写的笔记”里写三行：

```text
今天产出：
今天卡点：
明天第一件事：
```

---

## 9. 明日预告

Day 7 是休息日：

- 不推主线
- 定稿 W1 周复盘
- 用 30 分钟预览 W2：迭代器/生成器、装饰器、上下文管理器、dataclass、类型标注、日志、argparse

不要提前开始 W2 的项目改造。

---

## 10. 复盘问答

> 今天是补漏和重构日。下面这些问题决定你是“改完就算”还是“真的把工程做稳”。

### Q1. 重构时怎么判断“改坏了”？重构前要做什么保护？

重构的定义是：**不改变外部行为，只改善内部结构**。所以第一步不是改代码，而是建立“行为基线”：

1. 所有测试先跑绿。
2. 手工走一遍 CLI，记录关键输出。
3. 记下当前 Git commit hash，随时可以回退。

```bash
# 1. 跑全部测试，确认基线
# -m：运行模块；unittest：测试框架
# discover：自动发现；-s tests：从 tests/ 开始；-v：verbose
python3 -m unittest discover -s tests -v

# 2. 记录当前 commit，重构搞砸了可以回来
# --oneline：一行一个提交
# -1：只显示最后 1 条提交
git log --oneline -1

# 3. 重构前确保工作区干净，避免和已有改动混在一起
git status
```

重构节奏：

- 一次只改一个“味道”（命名、职责、重复代码）。
- 每改一步跑一次测试。
- 测试绿了再提交；不要攒一大坨再提交。

如果重构后测试挂了，先问：**是我改了行为，还是测试本身依赖了实现细节？** 前者回退，后者调整测试。

### Q2. 应该补哪些边界测试？怎么从需求推导测试用例？

用“等价类 + 边界值 + 错误路径”三件套：

| 类型 | 例子 |
|---|---|
| 正常值 | accuracy=0.9，batch_size=8 |
| 边界值 | accuracy=0、accuracy=1、batch_size=1 |
| 非法值 | accuracy=-0.1、accuracy=1.1、batch_size=0 |
| 空/缺失 | 空 JSON、空字符串、缺字段 |
| 重复/冲突 | 重复 ID、重复添加 |
| 损坏状态 | 非法 JSON、顶层不是列表 |
| 状态转换 | 删除后再查、删除后再删 |

从需求推导：

- “accuracy 必须在 0~1” → 测 0、1、-0.1、1.1。
- “ID 唯一” → 测重复添加。
- “文件损坏要报错” → 写非法 JSON 再读。

测试命名要说明场景：

```python
def test_accuracy_boundaries(self):
    """0 和 1 合法，越界抛 ValidationError。"""
    ...
```

工程习惯：一个测试只断言一个行为；失败时能从名字直接看出哪里坏了。

### Q3. 测试全绿，但代码仍然有 bug，可能是什么原因？

测试只能证明“你测过的路径是对的”，不能证明“没测过的路径是对的”。常见缺口：

1. **测试没覆盖真实入口**：只测了 service，没测 CLI 的输入解析。
2. **测试和实现用了同一个错误假设**：例如都假设 JSON 顶层一定是 list。
3. **外部环境差异**：路径、权限、编码、Windows/Linux。
4. **并发/时序**：W1 没测并发，单进程测试全绿不代表多进程安全。
5. **断言太弱**：只断言“不抛异常”，没断言结果内容。

补法：

- 加集成测试/手工冒烟（CLI 全流程）。
- 用真实但隔离的数据（临时目录）。
- 对关键输出做精确断言，不只断言类型。
- 记录 bug 的复现步骤，先写失败测试，再修。

### Q4. 怎么读一个失败的测试？从 `AssertionError` 到根因的排查流程

```text
FAIL: test_summary (tests.test_service.TestExperimentService)
AssertionError: 0.19999999999999998 != 0.2
```

步骤：

1. **看测试名**：`test_summary`，说明是汇总逻辑。
2. **看断言差异**：浮点数精度问题，还是算法错？
3. **最小复现**：用同样的输入直接调用 service，打印中间值。
4. **定位层**：是 service 算错，还是 storage 读错，还是 model 字段错？
5. **修实现或修测试**：如果是浮点精度，测试用 `assertAlmostEqual`；如果是算法错，修 service。

```python
# 浮点比较：不要用 ==，用 assertAlmostEqual
self.assertAlmostEqual(summary["average_loss"], 0.2)
```

工程习惯：失败信息要能 standalone 看懂；测试名 + 断言差异 + 输入数据，三者缺一不可。

### Q5. Git 历史很乱，要不要 rebase/squash？W1 阶段怎么处理？

W1 阶段：**不要重写历史**。原因：

- 你还在学习 Git，重写历史容易丢提交。
- 本地历史乱一点不影响项目质量；面试也不看 commit 数量。
- 真正的协作项目才需要严格的提交规范。

可以做的：

- 之后每次提交只做一件事，提交信息写清楚。
- 用 `git log --oneline --graph` 复盘自己的开发过程。
- 如果某次提交信息写错，用 `git commit --amend`（`--amend` 修改最后一次提交；已推送慎用）。

等工作后参与团队项目，再学 `git rebase -i`（交互式 rebase，压缩/重排提交）和 squash。现在先把“小步提交、可回滚”养成习惯。

### Q6. 口述练习说不清，说明什么？怎么补？

说不清通常不是“嘴笨”，而是以下之一：

1. **概念边界不清**：知道 `__eq__` 但说不清“身份 vs 值”。
2. **只知道结论，不知道原因**：知道要原子写，但说不出“不原子会怎样”。
3. **没有形成结构**：知识点是散的，无法按“问题 → 方案 → 代价”讲。

补法：

- 用“三句话模板”：**它解决什么问题 → 怎么做 → 代价/边界**。
- 画图：三个区域、依赖方向、请求生命周期。
- 关掉教程，从空白文件重写关键代码；写不出来就是没掌握。
- 找一个不懂的人讲一遍；对方能听懂，才算讲清。

示例：解释原子写

```text
问题：直接覆盖写，进程崩溃会留下半个文件。
做法：先写 tmp，再用 replace 原子替换。
代价：同文件系统才原子；并发写仍会丢更新。
```

### Q7. W1 出口标准有一项没过，能不能进 W2？取舍原则是什么？

可以进，但要把缺口**显式记录**，不能假装没发生。

取舍原则：

- **必须项**：不会就影响后续的，补完再走。例如“能独立写类/模块/异常”“Git 提交/分支/回滚”。
- **熟练项**：知道概念、但还不够快，可以带着走。例如 `@classmethod` 的细节、复杂冲突处理。
- **加分项**：W1 没要求的，直接砍。例如 pytest、类型标注、日志。

具体做法：

1. 在 `notes/2026-11-22.md` 的笔记区写“没达标：X，W2 第一天补 30 分钟”。
2. 把缺口排进 W2 第一天的主任务，而不是无限期拖延。
3. 如果缺口影响 W2 项目重构（例如不会模块/异常），先补再开始 W2 的新内容。

工程原则：**带着已知缺口前进，比假装完美更可靠**；但不能带着“不知道缺口在哪”前进。
