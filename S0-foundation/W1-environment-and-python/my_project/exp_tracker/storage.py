from pathlib import Path
import json
from .errors import StorageError,ValidationError,ExperimentNotFoundError
from .models import Experiment

class JsonExperimentStore:
    def __init__(self,data_file):
        self.data_file = Path(data_file)
        self._ensure_storage()

    def _ensure_storage(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._write_all()

    def _write_all(self,experiments):
        payload = [experiment.to_dict() for experiment in experiments]
        tmp_file = self.data_file.with_name(self.data_file.name+".tmp")

        try:
            tmp_file.write_text(
                json.dumps(payload, indent=2,ensure_ascii=False),
                encoding="utf-8",
            )
            tmp_file.replace(self.data_file)
        except OSError as e:
            raise StorageError(f'导入数据失败') from e

    def _read_all(self):
        try:
            text = self.data_file.read_text(encoding="utf-8")
        except OSError as e:
            raise StorageError(f'读取失败') from e

        try:
            raw_json = json.loads(text)
        except json.JSONDecodeError as e:
            raise StorageError(f'json不合法') from e

        if not isinstance(raw_json, list):
            raise StorageError(f'顶层需是列表')

        experiments = []
        for index,item in enumerate(raw_json):
            if not isinstance(item, dict):
                raise StorageError(f'第{index}条不是json')

            try:
                experiments.append(Experiment.from_dict(item))
            except ValidationError as e:
                raise StorageError(f'第{index}条数据val失败：{e}') from e

        return experiments

