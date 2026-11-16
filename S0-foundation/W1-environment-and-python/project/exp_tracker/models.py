"""
exp_tracker.models
==================

数据模型层：定义“一条实验记录长什么样”。

设计原则
--------
- 这个文件只关心数据本身：字段、校验、序列化/反序列化。
- 它不读写文件，不打印菜单，不询问用户输入。
- 这样模型可以被 storage、service、tests 独立复用。

W1 用普通类，是为了把 __init__ / self / __repr__ / __eq__ / classmethod
这些基础打牢。W2 会把它重构成 dataclass + 类型标注，你会更清楚
dataclass 自动帮你生成了哪些代码。
"""

from datetime import datetime
from uuid import uuid4

from .errors import ValidationError


class Experiment:
    """一条训练/评测实验记录。

    字段说明
    --------
    experiment_id : str
        唯一标识。创建时如果不传，自动生成 8 位十六进制 ID。
    name : str
        实验名，例如 "qwen2.5-7b-lr1e-4"。
    model : str
        模型名，例如 "Qwen2.5-7B-Instruct"。
    learning_rate : float
        学习率，必须 > 0。
    batch_size : int
        批大小，必须 > 0。
    accuracy : float
        准确率，必须在 0~1 之间。
    loss : float
        损失值，必须 >= 0。
    notes : str
        备注，最长 500 字符。
    created_at : str
        ISO 8601 时间字符串，例如 "2026-11-16T09:00:00"。
    """

    def __init__(
        self,
        name,
        model,
        learning_rate,
        batch_size,
        accuracy,
        loss,
        notes="",
        experiment_id=None,
        created_at=None,
    ):
        """创建一条实验记录，并立刻校验。

        参数没有写类型标注，是为了 W1 先专注“类/对象/异常”本身；
        W2 会补上完整的类型标注。
        """

        # ------------------------------------------------------------------
        # 1. 数值字段先做类型转换。
        #    用户输入/JSON 里的数字可能是字符串（"0.0001"），
        #    这里统一转成 float/int。
        #    如果转换失败，把底层 ValueError 包装成业务异常 ValidationError，
        #    并用 from exc 保留原始异常链，方便调试。
        # ------------------------------------------------------------------
        try:
            self.learning_rate = float(learning_rate)  # 学习率统一用 float
            self.batch_size = int(batch_size)          # batch size 统一用 int
            self.accuracy = float(accuracy)            # 准确率统一用 float
            self.loss = float(loss)                    # loss 统一用 float
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"数值字段格式不正确: {exc}") from exc

        # ------------------------------------------------------------------
        # 2. 字符串字段做清洗。
        #    - None 当成空字符串处理，避免 str(None) 变成 "None"。
        #    - strip() 去掉首尾空白，防止 "   " 被当成合法名字。
        # ------------------------------------------------------------------
        self.name = str(name).strip() if name is not None else ""
        self.model = str(model).strip() if model is not None else ""
        self.notes = str(notes).strip() if notes is not None else ""

        # ------------------------------------------------------------------
        # 3. ID 与创建时间。
        #    - 如果调用方传了 ID（例如从 JSON 读回来），就沿用。
        #    - 否则用 uuid4 生成 8 位十六进制；对学习项目足够唯一。
        #    - created_at 用本地时间的 ISO 字符串，方便直接写 JSON。
        # ------------------------------------------------------------------
        self.experiment_id = (
            str(experiment_id).strip() if experiment_id else uuid4().hex[:8]
        )
        self.created_at = (
            str(created_at).strip()
            if created_at
            else datetime.now().isoformat(timespec="seconds")
        )

        # ------------------------------------------------------------------
        # 4. 所有字段就位后，统一校验。
        #    校验失败会抛 ValidationError，对象不会被写入存储。
        # ------------------------------------------------------------------
        self.validate()

    def validate(self):
        """检查业务规则；不合法就抛 ValidationError。

        为什么把校验放在模型里，而不是 CLI 里？
        - CLI 只是入口之一；以后还可能有 Web API、批量导入脚本。
        - 把规则放在模型里，所有入口共享同一套校验，不会漏。
        """

        # 实验名不能为空，也不能太长（避免 JSON/日志里出现超长行）
        if not self.name:
            raise ValidationError("实验名 name 不能为空")
        if len(self.name) > 50:
            raise ValidationError("实验名 name 不能超过 50 个字符")

        # 模型名必填
        if not self.model:
            raise ValidationError("模型名 model 不能为空")

        # 学习率必须为正数
        if self.learning_rate <= 0:
            raise ValidationError("learning_rate 必须大于 0")

        # batch size 必须为正整数
        if self.batch_size <= 0:
            raise ValidationError("batch_size 必须大于 0")

        # 准确率是比例，必须在 0~1 之间
        if not 0 <= self.accuracy <= 1:
            raise ValidationError("accuracy 必须在 0 到 1 之间")

        # loss 不能为负
        if self.loss < 0:
            raise ValidationError("loss 不能为负数")

        # 备注长度限制
        if len(self.notes) > 500:
            raise ValidationError("notes 不能超过 500 个字符")

    def to_dict(self):
        """把对象转成可 JSON 序列化的字典。

        storage.py 会把这个字典写进 JSON 文件。
        字段名与 from_dict 保持一致，形成“序列化契约”。
        """
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

    @classmethod
    def from_dict(cls, data):
        """从字典创建 Experiment；用于读取 JSON。

        为什么用 @classmethod？
        - 如果以后有 TrainingExperiment(Experiment) 子类，
          调用 TrainingExperiment.from_dict(...) 时，cls 会自动是子类，
          不需要重写这个方法。
        """

        # 顶层必须是字典，否则无法按字段读取
        if not isinstance(data, dict):
            raise ValidationError("实验记录必须是字典")

        # 必填字段清单；缺一个就报清楚缺了哪些
        required_fields = [
            "name",
            "model",
            "learning_rate",
            "batch_size",
            "accuracy",
            "loss",
        ]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValidationError(f"实验记录缺少字段: {', '.join(missing)}")

        # notes / experiment_id / created_at 是可选字段，用 get 提供默认值
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

    @property
    def is_successful(self):
        """只读计算属性：准确率达到 0.9 视为成功。

        注意：访问时写 exp.is_successful，不要加括号。
        """
        return self.accuracy >= 0.9

    def summary(self):
        """返回一行适合终端显示的摘要。

        - :.3f 表示保留 3 位小数。
        - :g 用于学习率，避免 0.0001 被显示成 0.000。
        """
        return (
            f"[{self.experiment_id}] {self.name} | "
            f"model={self.model} | acc={self.accuracy:.3f} | "
            f"loss={self.loss:.3f} | lr={self.learning_rate:g} | "
            f"bs={self.batch_size}"
        )

    def __repr__(self):
        """给开发者看的精确表示；调试和容器打印会用到。"""
        return (
            f"Experiment(experiment_id={self.experiment_id!r}, "
            f"name={self.name!r}, model={self.model!r}, "
            f"learning_rate={self.learning_rate!r}, "
            f"batch_size={self.batch_size!r}, "
            f"accuracy={self.accuracy!r}, loss={self.loss!r})"
        )

    def __eq__(self, other):
        """按 experiment_id 判断是否是同一条实验。

        为什么按 ID 而不是按所有字段？
        - ID 是业务上的唯一标识；同一条记录修改了 accuracy 后，
          仍然应该被认为是同一条实验。
        - 如果按所有字段比较，测试里稍微改一个字段就会不相等，
          反而不符合业务语义。
        """
        if not isinstance(other, Experiment):
            # 返回 NotImplemented，让 Python 尝试对方的 __eq__；
            # 如果对方也不支持，最终结果是 False，而不是抛异常。
            return NotImplemented
        return self.experiment_id == other.experiment_id

    def __str__(self):
        """给用户看的可读字符串；print(exp) 会优先调用它。"""
        return self.summary()
