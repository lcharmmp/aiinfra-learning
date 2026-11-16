#!/usr/bin/env bash
# =============================================================================
# S0 W1 环境自检脚本
# =============================================================================
# 用法：
#   bash scripts/check_env.sh
#
# 这个脚本只读，不安装任何东西、不改配置。
# 它会检查：
#   1. 系统信息（CPU/内存/磁盘）
#   2. 本周需要的工具（python3/pip3/git/tmux/ssh）
#   3. Python 标准库模块（venv/json/pathlib/unittest）
#   4. ~/.ssh 权限
#   5. swap 状态（2G 内存的提醒）
#
# 注意：
#   - 用 `set -u` 让未定义变量报错；不用 `set -e`，
#     因为某个工具缺失时我们还想继续检查其他项。
# =============================================================================

set -u

echo "============================================================"
echo " S0 W1 环境自检"
echo " 日期: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "============================================================"

# -----------------------------------------------------------------------------
# 1. 系统信息
# -----------------------------------------------------------------------------
echo
echo "[1] 系统信息"
echo "------------------------------------------------------------"

# 内核与架构
uname -a

# CPU 核数；$(...) 会把命令输出嵌入字符串
echo "CPU 核数: $(nproc)"

# 内存与 swap；free -h 用人类可读单位
echo
echo "内存/交换分区:"
free -h

# 当前目录所在磁盘的剩余空间
echo
echo "磁盘（当前目录）:"
df -h .

# -----------------------------------------------------------------------------
# 2. 工具检查
# -----------------------------------------------------------------------------
echo
echo "[2] 工具检查"
echo "------------------------------------------------------------"

# 定义一个函数：检查命令是否存在，存在就打印版本
check_command() {
    local name="$1"          # 函数参数：命令名
    if command -v "$name" >/dev/null 2>&1; then
        # command -v 成功说明命令在 PATH 里
        printf "%-10s OK      %s\n" "$name" "$("$name" --version 2>&1 | head -n 1)"
    else
        printf "%-10s MISSING 请安装\n" "$name"
    fi
}

# python3 / pip3 / git 支持 --version
check_command python3
check_command pip3
check_command git

# tmux 用 -V，不认 --version
if command -v tmux >/dev/null 2>&1; then
    printf "%-10s OK      %s\n" "tmux" "$(tmux -V 2>&1 | head -n 1)"
else
    printf "%-10s MISSING 请安装: sudo apt install tmux\n" "tmux"
fi

# ssh 用 -V，而且输出到 stderr，所以要 2>&1
if command -v ssh >/dev/null 2>&1; then
    printf "%-10s OK      %s\n" "ssh" "$(ssh -V 2>&1 | head -n 1)"
else
    printf "%-10s MISSING 请安装: sudo apt install openssh-client\n" "ssh"
fi

# -----------------------------------------------------------------------------
# 3. Python 标准库检查
# -----------------------------------------------------------------------------
echo
echo "[3] Python 标准库检查"
echo "------------------------------------------------------------"

# 用 heredoc 把一段 Python 代码交给解释器执行；
# 这段代码只导入标准库，不依赖第三方包。
python3 - <<'PY'
import json
import pathlib
import sys
import unittest
import venv

print(f"Python 版本: {sys.version.split()[0]}")
print(f"解释器路径: {sys.executable}")
print("json      : OK")
print("pathlib   : OK")
print("unittest  : OK")
print("venv      : OK")
PY

# -----------------------------------------------------------------------------
# 4. SSH 权限检查
# -----------------------------------------------------------------------------
echo
echo "[4] SSH 目录与密钥权限"
echo "------------------------------------------------------------"

if [ -d "$HOME/.ssh" ]; then
    # 目录权限应为 700
    stat -c '%a %n' "$HOME/.ssh" 2>/dev/null || true

    # 私钥权限应为 600；公钥 644 可以接受
    find "$HOME/.ssh" -maxdepth 1 -type f -name 'id_*' -exec stat -c '%a %n' {} \; 2>/dev/null || true

    if [ -f "$HOME/.ssh/authorized_keys" ]; then
        stat -c '%a %n' "$HOME/.ssh/authorized_keys" 2>/dev/null || true
    else
        echo "提示: 还没有 ~/.ssh/authorized_keys（如果你要从本地免密登录服务器，Day 1 会配置）"
    fi
else
    echo "提示: ~/.ssh 不存在；Day 1 会生成密钥并创建目录"
fi

# -----------------------------------------------------------------------------
# 5. swap 提醒
# -----------------------------------------------------------------------------
echo
echo "[5] swap 检查"
echo "------------------------------------------------------------"

if swapon --show 2>/dev/null | grep -q .; then
    echo "swap 已启用:"
    swapon --show
else
    echo "swap 未启用。当前内存约 1.7G，W1 项目够用；"
    echo "W3 装 PyTorch 前建议加 2G swap（教程会讲，不要现在操作）。"
fi

# -----------------------------------------------------------------------------
# 6. 结论
# -----------------------------------------------------------------------------
echo
echo "============================================================"
echo " 自检完成。把关键输出记到 notes/2026-11-16.md。"
echo " 如果 python3/git/tmux/ssh 有 MISSING，先按提示安装，再开始 Day 1。"
echo "============================================================"
