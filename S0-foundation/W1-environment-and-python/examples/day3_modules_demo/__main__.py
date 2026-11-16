"""
让包可以直接用 `python3 -m day3_modules_demo` 运行。

Python 的 -m 机制：
- 如果给出的是包名，会去找包里的 __main__.py 并执行。
- 如果给出的是模块名（如 day3_modules_demo.main），会执行那个模块。

这个文件只是把 main.main() 转接一下，方便演示两种 -m 用法。
"""

from .main import main


if __name__ == "__main__":
    main()
