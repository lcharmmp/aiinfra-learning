"""
Day 3 示例：异常处理、自定义异常、异常链、try/except/else/finally。

运行方式（在 W1 目录下）：

    python3 examples/day3_exceptions_demo.py
"""

import json


# ----------------------------------------------------------------------
# 自定义异常：业务错误用业务异常表达
# ----------------------------------------------------------------------
class ConfigError(Exception):
    """配置加载失败。"""


class ValidationError(Exception):
    """数据校验失败。"""


# ----------------------------------------------------------------------
# 示例 1：捕获具体异常
# ----------------------------------------------------------------------
def safe_divide(a, b):
    """安全除法；除数为 0 时返回 None 并打印提示。"""

    try:
        result = a / b
    except ZeroDivisionError:
        # 只捕获“除数为 0”，其他错误继续向上抛
        print("  不能除以 0")
        return None
    else:
        # try 没有异常时执行
        print("  除法成功")
        return result
    finally:
        # 无论成功失败都执行；这里只是演示，实际常用于关闭文件/连接
        print("  safe_divide 结束")


# ----------------------------------------------------------------------
# 示例 2：捕获 ValueError，演示 else/finally
# ----------------------------------------------------------------------
def parse_int(text):
    """把字符串转成整数；失败返回 None。"""

    try:
        value = int(text)
    except ValueError:
        print(f"  {text!r} 不是合法整数")
        return None
    else:
        print(f"  解析成功: {value}")
        return value
    finally:
        print("  parse_int 结束")


# ----------------------------------------------------------------------
# 示例 3：异常链 raise ... from ...
# ----------------------------------------------------------------------
def load_json(path):
    """读取 JSON 配置；底层错误包装成 ConfigError。"""

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        # 抛业务异常，同时保留原始异常链
        raise ConfigError(f"无法加载配置: {path}") from exc


# ----------------------------------------------------------------------
# 示例 4：主动抛自定义异常
# ----------------------------------------------------------------------
def validate_accuracy(value):
    """校验准确率必须在 0~1 之间。"""

    if not isinstance(value, (int, float)):
        raise ValidationError(f"accuracy 必须是数字，收到 {type(value).__name__}")
    if not 0 <= value <= 1:
        raise ValidationError(f"accuracy 必须在 0 到 1 之间，收到 {value}")
    return float(value)


def main():
    print("=" * 60)
    print("1. safe_divide：捕获 ZeroDivisionError")
    print("=" * 60)
    print("10 / 2 =", safe_divide(10, 2))
    print("10 / 0 =", safe_divide(10, 0))

    print()
    print("=" * 60)
    print("2. parse_int：捕获 ValueError + else/finally")
    print("=" * 60)
    print("'123' ->", parse_int("123"))
    print("'abc' ->", parse_int("abc"))

    print()
    print("=" * 60)
    print("3. load_json：异常链")
    print("=" * 60)
    try:
        load_json("not-exist.json")
    except ConfigError as exc:
        print("业务异常:", exc)
        print("原始原因类型:", type(exc.__cause__).__name__)

    print()
    print("=" * 60)
    print("4. validate_accuracy：主动抛自定义异常")
    print("=" * 60)
    for value in [0.923, 1.5, "abc"]:
        try:
            print(f"  {value!r} ->", validate_accuracy(value))
        except ValidationError as exc:
            print(f"  {value!r} 校验失败: {exc}")

    print()
    print("=" * 60)
    print("5. 不推荐的裸 except（仅演示，不要模仿）")
    print("=" * 60)
    try:
        # 这里的 1 + "a" 会抛 TypeError
        1 + "a"
    except Exception as exc:
        # 至少用 Exception，而不是裸 except；
        # 更好的做法是捕获具体的 TypeError
        print("  捕获到:", type(exc).__name__, exc)


if __name__ == "__main__":
    main()
