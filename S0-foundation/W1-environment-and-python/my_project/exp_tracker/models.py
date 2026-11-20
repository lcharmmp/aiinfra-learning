import uuid
#原：from datetime import datetime
import datetime
from .errors import ValidationError
from uuid import UUID

class Experiment():
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
        #改了下，对照
        self.name = name.strip()
        self.model = model.strip()
        self.notes = notes.strip()

        try:
            self.learning_rate = float(learning_rate)
            self.batch_size = int(batch_size)
            self.accuracy = float(accuracy)
            self.loss = float(loss)
        except (ValueError, TypeError) as exc:
            raise ValidationError(f"数值字段格式错误：{exc}") from exc

        self.experiment_id = (
            str(experiment_id).strip() if experiment_id else uuid.uuid4().hex[:8]
        )
        self.created_at = (
            str(created_at).strip() if created_at else datetime.datetime.now().isoformat(timespec="seconds")
        )

        self.validate()

    def validate(self):
        #没写长度限制
        if not self.name:
            raise ValidationError("name needed")
        if not self.model:
            raise ValidationError("model needed")
        if self.learning_rate <= 0:
            raise ValidationError("learning rate needed to be greater than 0")
        if self.batch_size <= 0:
            raise ValidationError("batch size needed to be greater than 0")
        if not 0 <= self.accuracy <= 1:
            raise ValidationError("accuracy needs to be between 0 and 1")
        if self.loss <= 0:
            raise ValidationError("loss needs to be greater than 0")

    def to_dict(self):
        return {
            "name": self.name,
            "model": self.model,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "accuracy": self.accuracy,
            "loss": self.loss,
            "notes": self.notes,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValidationError("dict needed")
        required_keys = ["name", "model", "learning_rate", "batch_size", "accuracy", "loss", "notes", "experiment_id"]
        missing_keys = [key for key in required_keys if data.get(key) is None]
        if missing_keys:
            raise ValidationError(f"missing required keys: {missing_keys}")
        return cls(
            name=data["name"],
            model=data["model"],
            learning_rate=data["learning_rate"],
            batch_size=data["batch_size"],
            accuracy=data["accuracy"],
            loss=data["loss"],
            notes=data["notes"],
            experiment_id=data["experiment_id"],
            created_at=data["created_at"],
        )
    #property不加括号
    @property
    def is_successful(self):
        if self.accuracy >=0.8:
            return True
        return False

    def summary(self):
        return (f"[{self.experiment_id}]name={self.name} model={self.model} "
                f"accuracy={self.accuracy:.3f} loss={self.loss:.3f} "
                f"notes={self.notes} created_at={self.created_at}")
    #没写repr

    def __eq__(self, other):
        if not isinstance(other, Experiment):
            return NotImplemented
        return self.experiment_id == other.experiment_id

    def __str__(self):
        return self.summary()

