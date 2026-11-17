class Experiment:
    def __init__(self, name, accuracy):
        self.name = name
        # 这里会触发 accuracy 的 setter，而不是直接创建实例属性
        self.accuracy = accuracy

    @property
    def accuracy(self):
        """读取 accuracy 时调用。"""
        return self._accuracy

    @accuracy.setter
    def accuracy(self, value):
        """设置 accuracy 时调用；在这里做校验。"""
        if not isinstance(value, (int, float)):
            raise ValueError("accuracy 必须是数字")
        if not 0 <= value <= 1:
            raise ValueError("accuracy 必须在 0 到 1 之间")
        self._accuracy = float(value)   # 真正的存储放在 _accuracy

exp = Experiment("demo", 0.923)
print(exp.accuracy)      # 0.923

try:
    exp.accuracy = 0.5   # 触发校验，抛 ValueError
except ValueError as exc:
    print("设置失败:", exc)
print(exp.accuracy)