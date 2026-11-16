"""
exp_tracker.service
===================

业务逻辑层：把“用户想做的事”翻译成对存储/模型的调用。

为什么需要 service？
--------------------
CLI 不应该直接操作 storage：
- CLI 关心的是“怎么问用户、怎么显示结果”。
- storage 关心的是“怎么把数据写进 JSON”。
- 中间的业务规则（创建对象、汇总统计、校验）放在 service。

这样以后加 Web API 时，可以直接复用 service，不用重写业务逻辑。
"""

from .models import Experiment


class ExperimentService:
    """实验记录的业务用例。

    它持有一个 store（组合关系），只依赖 store 的这几个方法：
    - add(experiment)
    - list_all()
    - find_by_id(experiment_id)
    - delete(experiment_id)

    这种“只依赖需要的方法”的写法叫鸭子类型（duck typing）：
    只要对象长得像 store，就可以传进来，测试时可以用假对象替换。
    """

    def __init__(self, store):
        """保存 store 引用；不在这里创建 store，方便测试注入。"""
        self.store = store

    def add_experiment(
        self,
        name,
        model,
        learning_rate,
        batch_size,
        accuracy,
        loss,
        notes="",
    ):
        """创建并保存一条实验记录。

        参数校验由 Experiment 构造函数完成；
        如果校验失败，ValidationError 会直接向上抛，不会被这里吞掉。
        """

        # 先创建对象：构造函数里会做类型转换和业务校验
        experiment = Experiment(
            name=name,
            model=model,
            learning_rate=learning_rate,
            batch_size=batch_size,
            accuracy=accuracy,
            loss=loss,
            notes=notes,
        )

        # 再交给存储层持久化
        return self.store.add(experiment)

    def list_experiments(self):
        """返回所有实验记录。"""
        return self.store.list_all()

    def find_experiment(self, experiment_id):
        """按 ID 查找；找不到时由 store 抛 ExperimentNotFoundError。"""
        return self.store.find_by_id(experiment_id)

    def delete_experiment(self, experiment_id):
        """按 ID 删除；返回被删除的记录。"""
        return self.store.delete(experiment_id)

    def summary(self):
        """计算汇总统计。

        返回字典而不是字符串：
        - service 不应该关心终端怎么排版。
        - CLI 可以决定用表格、彩色输出还是 JSON。
        """

        experiments = self.store.list_all()

        # 空数据要返回稳定的结构，调用方不用做 None 判断
        if not experiments:
            return {
                "count": 0,
                "best_accuracy": None,
                "best_experiment": None,
                "average_loss": None,
                "models": [],
            }

        # 准确率最高的实验；max 的 key 是一个取字段的小函数
        best = max(experiments, key=lambda experiment: experiment.accuracy)

        # 平均 loss
        average_loss = sum(experiment.loss for experiment in experiments) / len(
            experiments
        )

        # 去重后排序，输出稳定
        models = sorted({experiment.model for experiment in experiments})

        return {
            "count": len(experiments),
            "best_accuracy": best.accuracy,
            "best_experiment": best.name,
            "average_loss": average_loss,
            "models": models,
        }
