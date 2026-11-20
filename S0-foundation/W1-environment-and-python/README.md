# S0 · W1：环境与 Python 基础

> 日期：**2026-11-16（周一）— 2026-11-22（周日）**
> 主线：SSH / tmux / Git / Python 虚拟环境 / 类与对象 / 模块 / 异常
> 交付：服务器可远程开发；一个带类、模块拆分、异常处理的 Python 小项目
> 每天：主任务 3h + 补课复盘 1h；其余时间自行安排

---

## 0. 本周先看这张图

```text
┌─────────────────────────────────────────────────────────────┐
│  W1 主线：从“会写脚本”到“能写一个小工程”                      │
│                                                             │
│  Day 1  SSH / tmux / Git 初始化 / 类入门                      │
│  Day 2  类与对象深化 / Git 分支、合并、回滚、远程              │
│  Day 3  模块与包 / 异常处理 / 项目骨架                        │
│  Day 4  项目 part1：errors.py / models.py / storage.py        │
│  Day 5  项目 part2：service.py / cli.py / tests / README      │
│  Day 6  补漏、重构、按出口标准自测                            │
│  Day 7  休息 + 周复盘                                         │
└─────────────────────────────────────────────────────────────┘
```

本周结束时要能独立完成：

```text
一个“实验记录器”小项目：
  用类表示实验记录
  用模块拆分 models / storage / service / cli
  用自定义异常处理校验和存储错误
  用 JSON 文件持久化
  用 unittest 测试
  用 Git 管理每一步
```

---

## 1. 每日时间块

| 时段 | 时长 | 做什么 | 注意 |
|---|---|---|---|
| 主任务 | 3h | 当天教程 + 动手写代码 | 只推进当天一个主线，不开新坑 |
| 补课复盘 | 1h | 查漏、写三行复盘、列明天第一件事 | 当天概念当天写进代码 |

建议节奏（可按课表平移，但顺序不要变）：

```text
09:00 - 12:00  主任务（中间休息 10 分钟）
21:00 - 22:00  补课与复盘
```

> 3 小时是主任务上限，不是底线。如果当天有课/考试，优先保主任务 3h，复盘可压缩，但不要连续两天为零。

---

## 2. 本周文件地图

| 文件/目录 | 用途 | 什么时候看 |
|---|---|---|
| [`day1-ssh-tmux-git.md`](./day1-ssh-tmux-git.md) | 周一教程：SSH、tmux、Git 初始化、类入门 | 11-16 上午 |
| [`day2-python-oop-git.md`](./day2-python-oop-git.md) | 周二教程：OOP 深化、Git 分支/回滚/远程 | 11-17 上午 |
| [`day3-modules-exceptions.md`](./day3-modules-exceptions.md) | 周三教程：模块、包、异常、项目骨架 | 11-18 上午 |
| [`day4-project-part1.md`](./day4-project-part1.md) | 周四教程：实现 errors/models/storage | 11-19 上午 |
| [`day5-project-part2.md`](./day5-project-part2.md) | 周五教程：实现 service/cli/tests | 11-20 上午 |
| [`day6-buffer-review.md`](./day6-buffer-review.md) | 周六：补漏、重构、自测 | 11-21 上午 |
| [`day7-rest.md`](./day7-rest.md) | 周日：休息 + 周复盘 | 11-22 |
| [`cheatsheets/`](./cheatsheets/) | 一页纸速查：SSH/tmux/Git、OOP、模块异常、Linux 生存命令 | 随时查 |
| [`scripts/check_env.sh`](./scripts/check_env.sh) | 检查服务器环境 | Day 1 第一件事 |
| [`notes/2026-11-16.md`](./notes/2026-11-16.md) — [`notes/2026-11-22.md`](./notes/2026-11-22.md) | 每天一个日期 note：自查 + 待我填写的笔记 | 每天结束前 |
| [`examples/`](./examples/) | 每天的小示例代码 | 看教程时对照跑 |
| [`git-practice/`](./git-practice/) | Git 分支/冲突/回滚练习场 | Day 2 |
| [`project/`](./project/) | 本周主项目“实验记录器”参考实现 | Day 4-5 |

> **参考实现的使用方式**：`project/` 里是完整代码。Day 4-5 先按教程自己写，卡住 15 分钟再看参考；不要一开始就复制。看懂后关掉文件，自己重敲一遍。
>
> **复盘问答**：每天教程末尾都有「复盘问答」，回答当天自查项和常见卡点里容易追问的问题。先自己答，再看解析。

---

## 3. 本周每日安排

### Day 1 · 2026-11-16 周一

**主任务（3h）：环境与第一版代码**

- 跑 `scripts/check_env.sh`，记录 Python/Git/tmux/SSH 版本、内存、磁盘。
- SSH：生成/确认密钥，配置 `~/.ssh/config`，做到免密登录。
- tmux：新建会话、运行一个长任务、分离、重连。
- Git：`git init -b main`（`-b` = `--initial-branch`，指定初始分支名）、`git status`、`git add`、`git commit`，完成第一次提交。
- 按 Day 1 的 4.7 节，把仓库推送到 GitHub（建议至少走通一次：SSH key → remote add → push）。
- Python 类入门：`class`、`__init__`、`self`、实例属性、方法；跑 `examples/day1_class_basics.py`。

**复盘（1h）：**

- 记下 SSH/tmux/Git 各一条最容易忘的命令。
- 把今天的三行写进 `notes/2026-11-16.md` 的“待我填写的笔记”。

**交付：** 环境自检记录 + 第一次 Git commit + GitHub 远程仓库（建议）+ 能跑通类示例。

---

### Day 2 · 2026-11-17 周二

**主任务（3h）：OOP 深化 + Git 工作流**

- 类属性 vs 实例属性、`__repr__`、`__eq__`。
- 继承：`super().__init__`；组合：一个类持有另一个类。
- `@property`、`@classmethod`、`@staticmethod` 各自什么时候用。
- 跑 `examples/day2_oop_advanced.py`，改 2 个地方观察输出。
- Git：分支、合并、冲突、`restore`、`reset`、`revert`、远程仓库。

**复盘（1h）：** 用一句话解释“继承”和“组合”的区别，各举项目里一个例子。

**交付：** `git-practice/` 里完成一次分支合并 + 一次冲突解决 + 一次安全回滚。

---

### Day 3 · 2026-11-18 周三

**主任务（3h）：模块、包、异常、项目骨架**

- 模块与包、`import` 的几种写法、`__name__ == "__main__"`。
- 绝对导入 vs 相对导入；为什么 `python -m package.module` 和 `python module.py` 不一样。
- 异常：`try/except/else/finally`、自定义异常、`raise ... from ...`。
- 跑 `examples/day3_modules_demo/` 和 `examples/day3_exceptions_demo.py`。
- 读 `project/exp_tracker/` 的骨架，画出模块依赖图。

**复盘（1h）：** 画一张图：`cli -> service -> storage -> models -> errors` 谁依赖谁。

**交付：** 能解释每个 `import` 语句；能说出项目每个文件的职责。

---

### Day 4 · 2026-11-19 周四

**主任务（3h）：项目 part1**

- 实现 `errors.py`：自定义异常层级。
- 实现 `models.py`：`Experiment` 类、校验、`to_dict/from_dict`。
- 实现 `storage.py`：JSON 读写、原子写入、查找、删除。
- 用 `python3 -c` 做手动 smoke test。
- 每完成一个文件提交一次 Git。

**复盘（1h）：** 记录至少 2 个你遇到的异常/边界问题。

**交付：** 能往 JSON 里存一条实验记录，并能读出来。

---

### Day 5 · 2026-11-20 周五

**主任务（3h）：项目 part2**

- 实现 `service.py`：业务逻辑、汇总统计。
- 实现 `cli.py` / `main.py`：菜单、输入校验、错误提示。
- 写 `tests/`：models/storage/service 各至少 2 个测试。
- 跑 `python3 -m unittest discover -s tests -v`。
- 补 README，提交，打 `v0.1.0` tag。

**复盘（1h）：** 把测试失败过的用例记下来，说明为什么失败。

**交付：** 项目可运行、测试全绿、Git 历史清晰。

---

### Day 6 · 2026-11-21 周六

**主任务（3h）：补漏与重构**

- 按 [`day6-buffer-review.md`](./day6-buffer-review.md) 的重构清单逐项检查。
- 补边界测试：空数据、重复 ID、损坏 JSON、非法 accuracy。
- 重跑本周所有示例和测试。
- 按 W1 出口标准逐项打勾；未达标项排进 W2 第一天。

**复盘（1h）：** 写周复盘初稿。

**交付：** W1 自测表 + 周复盘初稿。

---

### Day 7 · 2026-11-22 周日

**休息，不推主线。**

- 翻一遍本周笔记，把没想清楚的概念记下来。
- 写 W1 周复盘定稿，列 W2 第一件事。
- 不装新环境、不开新项目、不看新框架。

---

## 4. W1 出口标准

全部满足才算 W1 完成：

- [ ] 能不看教程，独立写出一个带类、模块拆分、异常处理的 Python 小项目
- [ ] 能解释 `__init__`、`self`、实例属性、类属性、继承、组合
- [ ] 能解释模块、包、`__name__ == "__main__"`、绝对导入与相对导入
- [ ] 能解释 `try/except/else/finally`、自定义异常、`raise ... from ...`
- [ ] 在服务器上独立完成 Git 提交、分支、合并、回滚
- [ ] SSH 免密可用；tmux 断开重连后任务还在

---

## 5. 本周 Git 提交节奏

建议至少 8 次提交，每次只做一件事：

```text
1. chore: 初始化学习仓库
2. feat: 完成 SSH/tmux 环境配置记录
3. feat: 添加 Python 类基础示例
4. feat: 实现 Experiment 模型与校验
5. feat: 实现 JSON 存储
6. feat: 实现 service 与 CLI
7. test: 添加 models/storage/service 单元测试
8. docs: 补 W1 README 与复盘
```

提交信息格式不强制，但要做到：**看 log 就知道每一步做了什么**。

---

## 6. 环境说明

当前服务器（已确认）：

| 项目 | 值 |
|---|---|
| CPU | 2 核 |
| 内存 | 1.7 GiB（无 swap） |
| 磁盘 | 40 GB，已用约 6.4 GB |
| Python | 3.10.12 |
| Git | 2.34.1 |
| tmux | 3.2a |
| SSH | OpenSSH 8.9p1 |
| pip | 22.0.2 |

注意：

- 2C2G 足够写代码、跑本周项目（纯标准库），但**不要**在本周装 PyTorch/跑模型。
- 内存只有 1.7G 且没有 swap；如果后续要装大包，W3 再按教程加 2G swap。
- 所有示例都只用标准库，`python3` 直接跑，不需要 `pip install`。

---

## 7. 开始之前

```bash
# 1. 进入 W1 目录
cd /root/aiinfra/S0-foundation/W1-environment-and-python

# 2. 跑环境自检
bash scripts/check_env.sh

# 3. 打开今天的教程
less day1-ssh-tmux-git.md
```

如果 `less` 不熟：`空格` 翻页，`b` 上一页，`/关键词` 搜索，`q` 退出。

现在开始 [Day 1](./day1-ssh-tmux-git.md)。
