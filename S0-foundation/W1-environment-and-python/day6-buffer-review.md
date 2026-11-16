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
python3 -m unittest discover -s tests -v

# 语法检查
python3 -m compileall -q exp_tracker main.py

# 非交互 CLI 冒烟
printf '2\n5\n0\n' | python3 main.py | tail -20

# Git 状态
git status
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
git add .
git commit -m "refactor: clean up W1 project and add edge-case tests"
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