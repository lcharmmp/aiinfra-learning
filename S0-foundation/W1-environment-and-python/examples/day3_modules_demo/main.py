"""
包内入口模块：演示相对导入。

运行方式（在 examples/ 目录下）：

    python3 -m day3_modules_demo.main

不要直接运行：

    python3 day3_modules_demo/main.py

直接运行会报：

    ImportError: attempted relative import with no known parent package

原因：
- `-m` 让 Python 把 day3_modules_demo 当作包来加载，包上下文存在，
  相对导入 `from .math_utils import add` 才能工作。
- 直接运行文件时，Python 只把 main.py 当普通脚本，没有“父包”概念，
  所以不知道 `.` 指的是谁。
"""

# 相对导入：`.` 表示当前包 day3_modules_demo
from .math_utils import add, multiply
from .text_utils import count_words


def main():
    """演示包内函数调用。"""

    print("add(2, 3) =", add(2, 3))
    print("multiply(4, 5) =", multiply(4, 5))
    print("count_words('hello ai infra') =", count_words("hello ai infra"))


if __name__ == "__main__":
    main()
