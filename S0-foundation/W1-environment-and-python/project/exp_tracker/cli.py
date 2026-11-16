"""
exp_tracker.cli
===============

命令行交互层：负责菜单、输入、输出、错误提示。

这一层只做三件事：
1. 问用户要什么。
2. 调用 service。
3. 把结果/错误打印出来。

它不直接读写 JSON，也不做业务校验——那些分别属于 storage 和 models。

W2 会用 argparse 把“菜单式交互”改成“子命令式 CLI”：
    python main.py add --name ... --model ...
    python main.py list
    python main.py summary
"""

from pathlib import Path

from .errors import ExperimentTrackerError
from .service import ExperimentService
from .storage import JsonExperimentStore


# ----------------------------------------------------------------------
# 数据文件路径
# ----------------------------------------------------------------------
# __file__           当前文件路径：.../project/exp_tracker/cli.py
# .resolve()         转成绝对路径，消除 .. 和符号链接
# .parent            上一级：.../project/exp_tracker
# .parent            再上一级：.../project
# / "data" / ...     拼出 .../project/data/experiments.json
#
# 这样不管你在哪个目录执行 python main.py，数据文件位置都固定，
# 不会因为“当前工作目录不同”而读写到别处。
DEFAULT_DATA_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "experiments.json"
)


# ----------------------------------------------------------------------
# 输入辅助函数
# ----------------------------------------------------------------------

def _prompt_text(label, allow_empty=False):
    """反复询问，直到拿到非空文本（或允许空字符串）。"""

    while True:
        value = input(label).strip()  # strip 去掉首尾空白
        if value or allow_empty:
            return value
        print("输入不能为空，请重试。")


def _prompt_float(label):
    """反复询问，直到拿到合法浮点数。"""

    while True:
        text = input(label).strip()
        try:
            return float(text)  # "0.0001" -> 0.0001
        except ValueError:
            # 不退出，提示后继续循环
            print(f"请输入数字，收到: {text!r}")


def _prompt_int(label):
    """反复询问，直到拿到合法整数。"""

    while True:
        text = input(label).strip()
        try:
            return int(text)  # "8" -> 8
        except ValueError:
            print(f"请输入整数，收到: {text!r}")


# ----------------------------------------------------------------------
# 输出辅助函数
# ----------------------------------------------------------------------

def _print_experiment(experiment):
    """打印一条实验的摘要和备注。"""
    print(experiment.summary())
    if experiment.notes:
        print(f"    备注: {experiment.notes}")


# ----------------------------------------------------------------------
# 各个菜单项的处理函数
# ----------------------------------------------------------------------

def _handle_add(service):
    """菜单 1：新增实验。"""

    print("\n== 新增实验 ==")

    # 文本字段
    name = _prompt_text("实验名: ")
    model = _prompt_text("模型名: ")

    # 数值字段：_prompt_float/_prompt_int 会处理格式错误
    learning_rate = _prompt_float("学习率（如 0.0001）: ")
    batch_size = _prompt_int("batch size: ")
    accuracy = _prompt_float("准确率（0~1）: ")
    loss = _prompt_float("loss: ")

    # 备注允许为空
    notes = _prompt_text("备注（可空）: ", allow_empty=True)

    # 业务校验在 Experiment 构造函数里；失败会抛 ValidationError，
    # 由 run_cli 的统一 except 捕获并打印。
    experiment = service.add_experiment(
        name=name,
        model=model,
        learning_rate=learning_rate,
        batch_size=batch_size,
        accuracy=accuracy,
        loss=loss,
        notes=notes,
    )

    print("\n已添加：")
    _print_experiment(experiment)


def _handle_list(service):
    """菜单 2：查看全部。"""

    experiments = service.list_experiments()

    if not experiments:
        print("\n暂无实验记录。")
        return

    print(f"\n共 {len(experiments)} 条实验记录：")
    for experiment in experiments:
        _print_experiment(experiment)


def _handle_find(service):
    """菜单 3：按 ID 查找。"""

    experiment_id = _prompt_text("实验 ID: ")

    # 找不到时 store 抛 ExperimentNotFoundError，由 run_cli 统一处理
    experiment = service.find_experiment(experiment_id)

    print("\n找到：")
    _print_experiment(experiment)


def _handle_delete(service):
    """菜单 4：按 ID 删除（带确认）。"""

    experiment_id = _prompt_text("要删除的实验 ID: ")

    # 先查出来给用户确认；不存在会在这一步就报错
    experiment = service.find_experiment(experiment_id)
    print("\n将要删除：")
    _print_experiment(experiment)

    confirm = input("确认删除？(y/N): ").strip().lower()
    if confirm != "y":
        print("已取消。")
        return

    service.delete_experiment(experiment_id)
    print("已删除。")


def _handle_summary(service):
    """菜单 5：汇总统计。"""

    data = service.summary()

    print("\n== 汇总 ==")
    print(f"实验总数: {data['count']}")

    if data["count"] == 0:
        print("还没有数据。")
        return

    print(
        f"最高准确率: {data['best_accuracy']:.3f}"
        f"（{data['best_experiment']}）"
    )
    print(f"平均 loss: {data['average_loss']:.4f}")
    print(f"涉及模型: {', '.join(data['models'])}")


# ----------------------------------------------------------------------
# 主循环
# ----------------------------------------------------------------------

MENU = """
================ 实验记录器 ================
1. 新增实验
2. 查看全部
3. 按 ID 查找
4. 按 ID 删除
5. 汇总统计
0. 退出
============================================
"""


def run_cli():
    """启动交互式命令行。

    结构：
    - 创建 store（负责 JSON）
    - 创建 service（负责业务）
    - 循环读取菜单选择
    - 统一捕获业务异常，打印友好提示
    """

    # 组合根：在这里把具体实现拼起来
    store = JsonExperimentStore(DEFAULT_DATA_FILE)
    service = ExperimentService(store)

    # 菜单编号 -> 处理函数
    actions = {
        "1": _handle_add,
        "2": _handle_list,
        "3": _handle_find,
        "4": _handle_delete,
        "5": _handle_summary,
    }

    print(f"数据文件: {DEFAULT_DATA_FILE}")

    while True:
        print(MENU)

        # 读取选择；Ctrl+C / Ctrl+D 都当作退出
        try:
            choice = input("请选择: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已退出。")
            break

        # 退出
        if choice == "0":
            print("再见。")
            break

        # 查找对应处理函数
        action = actions.get(choice)
        if action is None:
            print("无效选择，请输入 0-5。")
            continue

        # 统一捕获业务异常：
        # - 业务异常打印一行友好提示，不打印 traceback
        # - 其他异常不捕获，让它暴露出来，方便发现真正的 bug
        try:
            action(service)
        except ExperimentTrackerError as exc:
            print(f"\n操作失败: {exc}")
        except (KeyboardInterrupt, EOFError):
            # 用户在输入过程中按了 Ctrl+C / Ctrl+D，取消当前操作即可
            print("\n已取消当前操作。")
