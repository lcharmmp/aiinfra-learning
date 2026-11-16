"""
数学工具模块：演示“一个 .py 文件就是一个模块”。

这个模块不依赖项目的其他模块，可以独立导入和测试。
"""


def add(a, b):
    """返回两个数之和。"""
    return a + b


def multiply(a, b):
    """返回两个数之积。"""
    return a * b


def safe_divide(a, b):
    """安全除法：除数为 0 时抛 ZeroDivisionError。

    这里故意不吞异常，让调用方决定怎么处理。
    """
    if b == 0:
        raise ZeroDivisionError("除数不能为 0")
    return a / b


# 只有直接运行 `python math_utils.py` 时才执行；被 import 时不执行
if __name__ == "__main__":
    print("math_utils 自测：")
    print("add(1, 2) =", add(1, 2))
    print("multiply(3, 4) =", multiply(3, 4))
    print("safe_divide(10, 2) =", safe_divide(10, 2))
