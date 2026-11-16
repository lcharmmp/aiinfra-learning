#!/usr/bin/env python3
"""
实验记录器入口。

运行方式（在 project/ 目录下）：

    python3 main.py

为什么入口这么薄？
------------------
main.py 只负责“启动”，不写业务逻辑：
- 业务在 exp_tracker/service.py
- 存储在 exp_tracker/storage.py
- 交互在 exp_tracker/cli.py

这样你可以单独测试每个模块，而不需要启动整个菜单。

`if __name__ == "__main__":` 的作用：
- 直接运行本文件时，__name__ 是 "__main__"，会调用 run_cli()。
- 被其他模块 import 时，不会自动启动菜单。
"""

# 从包中导入 CLI 启动函数。
# 这里用绝对导入；运行 `python3 main.py` 时，main.py 所在目录
# 会被加入 sys.path，所以能找到 exp_tracker 包。
from exp_tracker.cli import run_cli


if __name__ == "__main__":
    run_cli()
