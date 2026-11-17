# AI Infra 学习仓库

> 主线：LLM 推理 Serving + Triton 算子
> 每天：主任务 3h + 补课复盘 1h；其余时间自行安排

完整计划见 [`ai-infra-learning-plan.md`](./ai-infra-learning-plan.md)。

---

## 当前阶段：S0 地基期 · W1 环境与 Python 基础

| 项目 | 内容 |
|---|---|
| 阶段 | S0 地基期 |
| 周次 | W1（第 1 周 / 共 6 周） |
| 日期 | **2026-11-16（周一）— 2026-11-22（周日）** |
| 本周主线 | SSH / tmux / Git / Python 虚拟环境 / 类与对象 / 模块 / 异常 |
| 本周交付 | 可远程开发；一个带类、模块拆分的 Python 小项目 |
| 本周教程入口 | [`S0-foundation/W1-environment-and-python/README.md`](./S0-foundation/W1-environment-and-python/README.md) |
| 今日任务 | 打开 [`day1-ssh-tmux-git.md`](./S0-foundation/W1-environment-and-python/day1-ssh-tmux-git.md)，从 0. 今日路线开始 |

先跑一次环境自检：

```bash
bash /root/aiinfra/S0-foundation/W1-environment-and-python/scripts/check_env.sh
```

---

## 目录结构

```text
/root/aiinfra/
├── ai-infra-learning-plan.md          # 总学习计划（总纲）
├── README.md                          # 本文件：仓库导航 + 当前阶段
├── PROGRESS.md                        # 里程碑、周进度、出口标准勾选
└── S0-foundation/                     # S0 地基期
    ├── README.md                      # S0 六周总览
    └── W1-environment-and-python/     # 第 1 周
        ├── README.md                  # W1 周计划（先看这个）
        ├── day1-ssh-tmux-git.md       # 周一：SSH / tmux / Git / 类入门
        ├── day2-python-oop-git.md     # 周二：类与对象深化 / Git 分支与回滚
        ├── day3-modules-exceptions.md # 周三：模块 / 包 / 异常 / 项目骨架
        ├── day4-project-part1.md      # 周四：项目实现（errors/models/storage）
        ├── day5-project-part2.md      # 周五：项目实现（service/cli/tests）
        ├── day6-buffer-review.md      # 周六：补漏、重构、自测
        ├── day7-rest.md               # 周日：休息 + 周复盘
        ├── cheatsheets/               # 一页纸速查表
        ├── scripts/                   # 环境检查脚本
        ├── notes/                     # 每天一个日期 note（自查 + 笔记）
        ├── examples/                  # 每天的小示例代码
        └── project/                   # 本周主项目：实验记录器
```

---

## 怎么用这套材料

1. **先读当天的教程，再动手。** 每天先看“今日路线”和“时间块”，按主任务 3h + 复盘 1h 执行。
2. **参考实现不要直接抄。** `project/` 里是完整参考代码；Day 4-5 先自己写，卡住 15 分钟再看参考，并把自己的错误记进复盘。
3. **每段代码都自己敲一遍。** 本仓库代码只依赖 Python 标准库，2C2G 服务器可直接跑；不需要装 PyTorch。
4. **每天结束前提交一次 Git。** 即使只改了一行注释，也提交；提交信息写清“做了什么”。
5. **卡住超过 2 天就换方法。** 查文档、看源码、最小复现、提问，不要死磕。

---

## 本周时间表

| 日期 | 星期 | 主任务（3h） | 复盘（1h） | 产出 |
|---|---|---|---|---|
| 11-16 | 周一 | SSH、tmux、Git 初始化、类入门 | 环境自检 + 三行复盘 | 环境可用；第一次 commit |
| 11-17 | 周二 | 类与对象深化、Git 分支/回滚/远程 | OOP 自查 + 三行复盘 | 分支/冲突练习完成 |
| 11-18 | 周三 | 模块/包/导入、异常、项目骨架 | 导入实验 + 三行复盘 | 模块依赖图 |
| 11-19 | 周四 | 项目 part1：errors/models/storage | 存储边界 + 三行复盘 | 存取跑通 |
| 11-20 | 周五 | 项目 part2：service/cli/tests | 测试结果 + 三行复盘 | 项目可运行、测试全绿 |
| 11-21 | 周六 | 补漏、重构、W1 自测 | 周复盘初稿 | 自测表 + 更干净的代码 |
| 11-22 | 周日 | 休息（不推主线） | W1 周复盘定稿 | 复盘定稿 |

---

## 学习原则

- 同一时间只推进一个主线阶段。
- 时间不够时砍范围，不推日期。
- 验收看交付物，不看课时。
- 所有代码和实验结果进 Git；数字必须可复现。
- 连续两天卡同一问题，第三天必须换方法。

---

## 文档约定（现行与后续都遵守）

- **每条 shell 命令都要在注释里拆开解释参数/选项**，不能只写“创建/提交/查看”这种结论。
- 命令里出现的缩写、短选项、长选项、路径、重定向符、通配符，都要说明含义。
- 示例：

  ```bash
  # git init：在当前目录创建 Git 仓库（生成 .git/）
  # -b main：-b 是 --initial-branch 的缩写，指定初始分支名为 main
  #          旧版 Git 没有 -b，改用 git init && git branch -m main
  git init -b main
  ```

- 不确定的参数先查 `man <命令>` 或 `<命令> --help`，再写进教程。
