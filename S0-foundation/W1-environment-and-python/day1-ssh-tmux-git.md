# Day 1 · SSH / tmux / Git 初始化 / Python 类入门

> 阶段：S0 地基期 · W1 第 1 天
> 日期：2026-11-16（周一）
> 今日交付：环境自检记录 + SSH 免密 + tmux 断线重连 + 第一次 Git commit + 能跑通一个类

---

## 0. 今日路线

| 时间 | 内容 | 产出 |
|---|---|---|
| 0:00 - 0:15 | 跑环境自检，记录版本/内存/磁盘 | `notes/2026-11-16.md` 笔记区 |
| 0:15 - 1:10 | SSH：密钥、免密、config、排错 | 能 `ssh aiinfra` 免密登录 |
| 1:10 - 1:45 | tmux：会话/窗口/窗格、断线重连 | 一个后台还在跑的任务 |
| 1:45 - 2:30 | Git：init/add/commit/log/diff | 第一次 commit |
| 2:30 - 3:00 | Python 类入门：`class`、`__init__`、`self` | 跑通 `examples/day1_class_basics.py` |
| 3:00 - 4:00 | 补课 + 三行复盘 | 今日复盘 |

> 如果你现在就是通过 SSH 登录这台服务器的，SSH 部分可以只做“检查 + 配置别名 + 验证”，不必重新买服务器。密钥对的意义是：**以后从你的本地电脑免密连服务器**。

---

## 1. 先建立心智模型

今天会同时出现四个东西，先分清它们各自解决什么问题：

```text
你的本地电脑                        远程 Linux 服务器
┌──────────────┐                  ┌──────────────────────┐
│ 终端 / VS Code│ ─── SSH ───────▶ │ 2 核 2G，跑代码和 Git │
│ 浏览器        │                  │ tmux 里的进程不会断   │
└──────────────┘                  └──────────────────────┘
        │
        │ Git
        ▼
┌──────────────┐
│ 本地/远程仓库 │  记录每一次代码变化，可回滚、可分支
└──────────────┘
```

- **SSH**：一条加密通道，让你在本地终端里操作远程服务器。
- **tmux**：服务器上的“虚拟终端管家”。SSH 断了，tmux 里的进程还在跑。
- **Git**：代码的时间机器。记录每次提交，能看历史、能回滚、能开分支。
- **Python 类**：把“数据 + 操作数据的函数”打包在一起，是后面 PyTorch `nn.Module`、数据集类、服务配置类的基础。

一句话记住：

> SSH 解决“怎么连”，tmux 解决“断了怎么办”，Git 解决“改坏了怎么办”，类解决“代码怎么组织”。

---

## 2. SSH：从本地免密登录服务器

### 2.1 先检查客户端

在**你的本地电脑**上打开终端（Windows 用 PowerShell 或 Git Bash，macOS/Linux 用 Terminal），执行：

```bash
# 查看 SSH 客户端版本；有输出说明已安装
ssh -V
```

预期输出类似：

```text
OpenSSH_8.9p1 Ubuntu-3ubuntu0.18, OpenSSL 3.0.2
```

如果提示 `command not found`：

- Windows：安装 Git for Windows，或用“设置 → 应用 → 可选功能 → OpenSSH 客户端”。
- macOS：通常自带；没有就 `brew install openssh`。
- Ubuntu/Debian：`sudo apt update && sudo apt install openssh-client`。

### 2.2 密钥对是什么

SSH 默认用密码登录。密码的缺点：

- 弱密码容易被爆破。
- 每次都要输入，自动化脚本很麻烦。
- 很多平台（GitHub、GitLab）根本不接受密码。

密钥对是一对文件：

```text
~/.ssh/id_ed25519       私钥：留在本地，绝对不能给别人
~/.ssh/id_ed25519.pub   公钥：可以随便给服务器/GitHub
```

类比：**公钥是锁，私钥是钥匙**。你把锁装到服务器上，只有拿着钥匙的你能打开。

### 2.3 生成密钥

在**本地电脑**执行：

```bash
# -t ed25519：使用现代推荐的 Ed25519 算法，比 RSA 更短更安全
# -C "aiinfra-w1"：给密钥加一个注释，方便以后辨认用途
ssh-keygen -t ed25519 -C "aiinfra-w1"
```

交互过程：

```text
Enter file in which to save the key (/home/you/.ssh/id_ed25519):
```

直接回车，使用默认路径。如果已经有同名密钥，会问是否覆盖；**不要覆盖旧的**，可以换个名字，例如 `/home/you/.ssh/id_ed25519_aiinfra`。

```text
Enter passphrase (empty for no passphrase):
```

给私钥加一个口令（passphrase）。建议设置：即使私钥文件泄露，没有口令也不能直接用。输入时屏幕不显示字符，正常。

```text
Your identification has been saved in /home/you/.ssh/id_ed25519
Your public key has been saved in /home/you/.ssh/id_ed25519.pub
```

查看公钥：

```bash
# 打印公钥内容；以 ssh-ed25519 开头的一整行就是公钥
cat ~/.ssh/id_ed25519.pub
```

输出类似：

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... aiinfra-w1
```

> 安全规则：**只把 `.pub` 文件的内容给别人，永远不要发没有 `.pub` 的私钥文件。**

### 2.4 把公钥放到服务器

最简单的方式（本地电脑执行）：

```bash
# ssh-copy-id：把公钥追加到远程用户的 ~/.ssh/authorized_keys
# -i ~/.ssh/id_ed25519.pub：指定要复制的公钥文件（-i = identity file）
# root@1.2.3.4：远程用户名 root + @ + 服务器 IP
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@1.2.3.4
```

第一次会要求输入服务器密码。成功后测试：

```bash
# ssh：SSH 客户端
# root@1.2.3.4：用户名 root + @ + 服务器 IP
# 成功的话这次不再问密码
ssh root@1.2.3.4
```

如果 `ssh-copy-id` 不存在（Windows 某些环境），手动做：

```bash
# 1) 在本地打印公钥并复制整行
cat ~/.ssh/id_ed25519.pub

# 2) 登录服务器
ssh root@1.2.3.4

# 3) 在服务器上创建目录并追加公钥
# mkdir -p：创建目录；-p = --parents，父目录不存在时逐级创建，已存在不报错
mkdir -p ~/.ssh

# chmod 700：所有者可读(4)+写(2)+执行(1)=7，组和其他人无权限
chmod 700 ~/.ssh

# echo '...'：输出这一行
# >> ~/.ssh/authorized_keys：追加写入；>> 是追加，> 会覆盖
echo '把刚才复制的整行公钥粘贴到这里' >> ~/.ssh/authorized_keys

# chmod 600：所有者可读(4)+写(2)=6，组和其他人无权限
chmod 600 ~/.ssh/authorized_keys
```

注意：

- `>>` 是追加，不要用 `>` 覆盖，否则会把已有的公钥清空。
- `~/.ssh` 权限必须是 `700`，`authorized_keys` 必须是 `600`，否则 SSH 会拒绝使用公钥。
- 如果服务器是云厂商，检查安全组是否放行 22 端口；如果改了 SSH 端口，连接时加 `-p 端口号`（`-p` = port，小写；`scp` 里端口用大写 `-P`）。

### 2.5 配置 SSH 别名

每次都敲 `ssh root@1.2.3.4` 很烦。编辑本地文件 `~/.ssh/config`：

```bash
# 创建或打开配置文件
# nano：简单文本编辑器
#   Ctrl+O 保存（然后回车确认文件名），Ctrl+X 退出
# Linux/macOS
nano ~/.ssh/config
# Windows 可用记事本打开 C:\Users\你的用户名\.ssh\config
```

写入：

```sshconfig
Host aiinfra
    HostName 1.2.3.4          # 服务器 IP 或域名
    User root                 # 登录用户名
    Port 22                   # SSH 端口；如果改了端口，这里同步改
    IdentityFile ~/.ssh/id_ed25519   # 私钥路径
    ServerAliveInterval 60    # 每 60 秒发一次心跳，防止空闲被断开
    ServerAliveCountMax 3     # 连续 3 次心跳失败才断开
```

保存后设置权限（Linux/macOS）：

```bash
chmod 600 ~/.ssh/config
```

以后只需：

```bash
# 直接使用别名登录
ssh aiinfra
```

### 2.6 验证与排错

验证免密：

```bash
# -v：verbose，打印详细握手过程
# 成功时最后会看到 Authentication succeeded (publickey)
# 想看得更细可以用 -vv 或 -vvv（调试用，输出很长）
ssh -v aiinfra
```

常见错误对照表：

| 现象 | 原因 | 解决 |
|---|---|---|
| `Permission denied (publickey)` | 公钥没放对、权限不对、用户名错 | 检查 `~/.ssh/authorized_keys` 内容；`chmod 700 ~/.ssh`、`chmod 600 ~/.ssh/authorized_keys` |
| `Connection refused` | 服务器没开 SSH、端口错、防火墙/安全组拦截 | `systemctl status ssh`；检查端口和安全组 |
| `Connection timed out` | IP 错、网络不通、安全组没放行 | `ping 服务器IP`；检查云厂商安全组 |
| `WARNING: UNPROTECTED PRIVATE KEY FILE` | 私钥权限太宽 | `chmod 600 ~/.ssh/id_ed25519` |
| 一直提示输入密码 | 公钥没生效 | `ssh -v` 看是否尝试了 publickey；检查 `authorized_keys` 是否在正确用户目录 |
| `Host key verification failed` | 服务器重装/换 IP，known_hosts 里旧指纹不匹配 | 确认安全后 `ssh-keygen -R 服务器IP` 删除旧记录 |

安全规则：

- 私钥文件权限 `600`，`.ssh` 目录 `700`。
- 给私钥设 passphrase；如果嫌麻烦，可以用 `ssh-agent` 缓存。
- 不要在公共电脑上生成或保存私钥。
- 服务器可以禁用密码登录（`PasswordAuthentication no`），但**先确认密钥登录成功再改**，否则会把自己锁在外面。

### 2.7 今日 SSH 动手任务

1. 在本地生成密钥（如果已有，跳过）。
2. 把公钥放到服务器，做到 `ssh aiinfra` 不输密码。
3. 在 `~/.ssh/config` 里加 `ServerAliveInterval 60`。
4. 故意把私钥权限改成 `644`，再 `ssh` 一次，观察报错；然后改回 `600`。
5. 把这条排错过程写进今日复盘。

---

## 3. tmux：让任务在断线后继续跑

### 3.1 为什么需要 tmux

如果你直接在 SSH 会话里跑一个 2 小时的任务：

```bash
python train.py
```

然后网络断了、笔记本合盖了、Wi-Fi 切了——SSH 会话结束，`python train.py` 通常会被挂断（SIGHUP），任务白跑。

tmux 的做法：

```text
SSH 连接 ──▶ tmux server（在服务器上常驻）
                ├── session w1
                │     ├── window 0: 代码
                │     └── window 1: 训练/压测
                └── session w2
```

你连上的是 tmux 的“显示器”，不是直接连进程。SSH 断了，tmux server 和里面的进程还在；重连后 `tmux attach` 就能看到原来的屏幕。

### 3.2 三个层级

| 层级 | 是什么 | 类比 |
|---|---|---|
| session | 一个工作空间，可以整体分离/重连 | 一个项目 |
| window | session 里的标签页 | 浏览器的标签页 |
| pane | window 里拆分的区域 | 分屏 |

前缀键（prefix）默认是 `Ctrl+b`。所有快捷键都要先按 `Ctrl+b`，**松开**，再按下一个键。

### 3.3 基本命令

在服务器终端执行：

```bash
# tmux -V：-V = version，打印 tmux 版本（大写 V）
tmux -V

# tmux new：新建一个会话
# -s w1：-s = session name，会话名为 w1
tmux new -s w1

# sleep 300：暂停 300 秒（5 分钟），模拟一个长任务
sleep 300

# 分离：先按 Ctrl+b，松开，再按 d
# 回到普通 shell 后，查看会话列表

# tmux ls：list sessions，列出所有会话
tmux ls

# tmux attach：连接到一个已存在的会话
# -t w1：-t = target session，目标会话名为 w1
tmux attach -t w1

# tmux kill-session：彻底结束一个会话
# -t w1：目标会话名；里面的进程也会结束
tmux kill-session -t w1
```

常用快捷键：

| 操作 | 按键 |
|---|---|
| 分离会话 | `Ctrl+b` 然后 `d` |
| 新建窗口 | `Ctrl+b` 然后 `c` |
| 重命名窗口 | `Ctrl+b` 然后 `,` |
| 下一个/上一个窗口 | `Ctrl+b` 然后 `n` / `p` |
| 列出窗口 | `Ctrl+b` 然后 `w` |
| 关闭当前窗口 | `Ctrl+b` 然后 `&` |
| 垂直分屏 | `Ctrl+b` 然后 `%` |
| 水平分屏 | `Ctrl+b` 然后 `"` |
| 在窗格间切换 | `Ctrl+b` 然后方向键 |
| 当前窗格最大化/还原 | `Ctrl+b` 然后 `z` |
| 关闭当前窗格 | `Ctrl+b` 然后 `x` |
| 向上翻页 | `Ctrl+b` 然后 `[`，用 PageUp/PageDown，按 `q` 退出 |

### 3.4 今日 tmux 动手任务

```bash
# 1. 新建会话
tmux new -s w1

# 2. 在会话里跑一个会持续输出的命令
while true; do date; sleep 2; done

# 3. 按 Ctrl+b，松开，按 d 分离

# 4. 确认会话还在
tmux ls

# 5. 重新连接，应该能看到时间还在更新
tmux attach -t w1

# 6. 按 Ctrl+c 停止循环

# 7. 再开两个窗格练手
#    Ctrl+b %   垂直分屏
#    Ctrl+b "  水平分屏
#    Ctrl+b 方向键 切换
#    Ctrl+b x  关闭
```

常见问题：

| 现象 | 原因 | 解决 |
|---|---|---|
| `no server running on /tmp/tmux-...` | 没有会话，或 tmux server 已退出 | `tmux new -s w1` |
| `sessions should be nested with care, unset $TMUX to force` | 你已经在 tmux 里，又想嵌套 tmux | 先 `unset TMUX`，或不要嵌套 |
| 按 `Ctrl+b` 没反应 | 前缀键被其他软件占用，或按键顺序不对 | 先按住 Ctrl 再按 b，松开后再按功能键 |
| 滚轮不能翻页 | tmux 默认不跟随鼠标 | `Ctrl+b [` 进入复制模式，或用鼠标模式配置 |
| `tmux attach` 后屏幕乱码 | 终端类型/字体问题 | 退出重连；设置 `TERM=xterm-256color` |

> 从今天开始，**所有超过 5 分钟的任务都放进 tmux**。这是后面在 4090 上跑压测、训练时的保命习惯。

---

## 4. Git：第一次提交

### 4.1 Git 的三个区域

```text
工作区（你改的文件）
    │  git add
    ▼
暂存区（准备提交的内容）
    │  git commit
    ▼
本地仓库（历史快照）
    │  git push
    ▼
远程仓库（GitHub/Gitee）
```

关键理解：

- `git add` 是“挑选这次要提交哪些改动”，不是“保存文件”。
- `git commit` 是把暂存区打成一个快照，带一条说明。
- 每次 commit 都有一个唯一哈希，可以回滚到任意一次。
- `.git/` 目录是仓库数据库，不要手动改里面的文件。

### 4.2 配置身份

Git 每次提交都会记录“作者名”和“作者邮箱”。先配置一次，之后所有仓库共用。

```bash
# git config：读取或写入 Git 配置
# --global：写入 ~/.gitconfig，对当前用户的所有仓库生效
#           不加 --global 时，只写入当前仓库的 .git/config
# user.name：配置项名称，提交记录里的作者名
# "Your Name"：配置值
git config --global user.name "Your Name"

# user.email：提交记录里的作者邮箱
# GitHub 可以用“用户名@users.noreply.github.com”，避免公开真实邮箱
git config --global user.email "you@example.com"

# --list：列出当前生效的所有配置项
# 不加 --global 则只列当前仓库的配置
git config --global --list

# 可选：设置以后 git init 的默认初始分支名
# init.defaultBranch：配置项名称
# main：值
# 设置后，以后执行 git init（不带 -b）也会默认创建 main 分支
git config --global init.defaultBranch main
```

如果提示 `Please tell me who you are`，就是 `user.name` 和 `user.email` 没配。

---

### 4.3 在练习目录完成第一次提交

我们专门准备了 `git-practice/`，先在这里练，不污染主项目。

#### 4.3.1 初始化仓库

```bash
# cd：change directory，切换当前目录
# 后面的路径是 git-practice 的绝对路径
cd /root/aiinfra/S0-foundation/W1-environment-and-python/git-practice

# git init：在当前目录创建一个新的 Git 仓库
#          执行后会出现隐藏目录 .git/，它保存提交历史、分支、配置等
# -b main：指定初始分支名为 main
#          -b 是 --initial-branch 的缩写（Git 2.28+）
#          不写 -b 时，旧版 Git 默认用 master；新版可能给出提示
#          如果你的 Git 版本低于 2.28，改用：
#            git init
#            git branch -m main
#          git branch -m main 里的 -m 是 --move，重命名当前分支
git init -b main
```

#### 4.3.2 查看状态、创建文件

```bash
# git status：显示当前分支，以及三类文件：
#   1. Changes to be committed：已暂存，下一次 commit 会包含
#   2. Changes not staged for commit：已跟踪但未暂存
#   3. Untracked files：Git 还没跟踪的新文件
git status

# cat：把标准输入或文件内容输出到标准输出
# > hello.py：重定向并“覆盖”写入 hello.py
#             单个 > 是覆盖；>> 是追加
# <<'PY'：here-document，把接下来的内容作为标准输入，直到单独一行 PY
#         'PY' 两边的引号表示不做变量替换
#         如果写成 <<PY（不加引号），$变量 会被 shell 展开
cat > hello.py <<'PY'
# 这是 Git 练习用的最小 Python 文件
# 打印一句话，证明文件内容被正确提交
print("hello, ai infra")
PY

# 再看一次状态：hello.py 应该出现在 Untracked files 里
git status
```

#### 4.3.3 暂存与提交

```bash
# git add：把文件的当前内容加入“暂存区/索引”
# hello.py：要暂存的文件名
# 注意：git add 不是提交，只是挑选下一次 commit 要包含哪些改动
git add hello.py

# 再看状态：hello.py 应该出现在 Changes to be committed 里
git status

# git commit：把暂存区的内容生成一个提交（一次快照）
# -m "..."：在命令行直接提供提交说明
#           不加 -m 时，Git 会打开默认编辑器让你写说明
# 提交说明建议写“做了什么”，例如 feat: add hello.py
git commit -m "feat: add hello.py for git practice"

# git log：查看提交历史
# --oneline：每个提交压缩成一行，显示“短哈希 + 提交说明”
git log --oneline
```

预期输出类似：

```text
a1b2c3d (HEAD -> main) feat: add hello.py for git practice
```

- `a1b2c3d` 是提交哈希的前 7 位，唯一标识这次提交。
- `HEAD -> main` 表示当前检出的分支是 `main`。
- `HEAD` 是指向“当前提交”的指针，切换分支/提交时会移动。

#### 4.3.4 修改文件、查看差异

```bash
# sed：stream editor，流编辑器
# -i：in-place，直接修改原文件（不是只输出到终端）
#     macOS 自带的 sed 要求写成 -i ''，Linux 不需要
# 's/hello, ai infra/hello, world/'：substitute 命令
#     把每行第一个 hello, ai infra 替换成 hello, world
sed -i 's/hello, ai infra/hello, world/' hello.py

# git diff：显示“工作区 vs 暂存区”的差异
#           也就是还没 git add 的改动
git diff

# git add：把修改后的版本重新加入暂存区
git add hello.py

# git diff --staged：显示“暂存区 vs 上一次提交”的差异
# --staged 是 --cached 的同义词
git diff --staged

# git commit：生成第二次提交
# -m：提交说明
git commit -m "docs: update greeting"

# git log：查看历史
# --oneline：一行一个提交
# --graph：用 ASCII 字符画出分支/合并图
git log --oneline --graph
```

---

### 4.4 常用命令速查（每个参数都解释）

| 命令 | 参数解释 | 作用 |
|---|---|---|
| `git status` | 无参数 | 看当前分支、暂存区、未暂存、未跟踪文件 |
| `git status --short` | `--short`：用两列短格式输出 | 紧凑查看状态 |
| `git add hello.py` | `hello.py`：要加入暂存区的文件 | 暂存单个文件 |
| `git add .` | `.`：当前目录及子目录 | 暂存当前目录所有改动（先确认没有密钥/大文件） |
| `git add -A` | `-A`：--all，所有改动（含删除） | 暂存整个仓库的改动 |
| `git diff` | 无参数 | 工作区 vs 暂存区 |
| `git diff --staged` | `--staged`：暂存区 vs 最后一次提交 | 看这次要提交什么 |
| `git commit -m "msg"` | `-m`：message，直接给提交说明 | 提交暂存区 |
| `git commit --amend` | `--amend`：修改最后一次提交 | 改提交说明/补文件（已推送慎用） |
| `git log --oneline` | `--oneline`：一行一个提交 | 看简洁历史 |
| `git log --oneline --graph --all` | `--graph`：画图；`--all`：所有分支 | 看完整分支历史 |
| `git show <hash>` | `<hash>`：提交哈希 | 看某次提交的具体改动 |
| `git restore <file>` | `restore`：恢复；`<file>`：目标文件 | 丢弃工作区改动 |
| `git restore --staged <file>` | `--staged`：只恢复暂存区 | 取消暂存，工作区不变 |
| `git rm --cached <file>` | `--cached`：只从索引删除，保留工作区文件 | 停止跟踪文件 |
| `git branch` | 无参数：列出本地分支 | 查看分支 |
| `git branch -a` | `-a`：--all，含远程分支 | 查看所有分支 |
| `git switch <branch>` | `<branch>`：目标分支 | 切换分支 |
| `git switch -c <branch>` | `-c`：--create，新建并切换 | 创建新分支 |
| `git branch -d <branch>` | `-d`：--delete，仅删除已合并分支 | 删除分支 |
| `git branch -D <branch>` | `-D`：强制删除未合并分支 | 危险，确认后再用 |
| `git branch -m <new>` | `-m`：--move，重命名当前分支 | 改分支名 |
| `git branch -M <new>` | `-M`：强制重命名（覆盖同名） | 把 master 改成 main |
| `git remote add origin <url>` | `add`：新增；`origin`：远程名；`<url>`：地址 | 关联远程仓库 |
| `git remote -v` | `-v`：verbose，显示 fetch/push 两个 URL | 查看远程地址 |
| `git remote set-url origin <url>` | `set-url`：修改远程地址 | 修正写错的 URL |
| `git push -u origin main` | `-u`：设置上游；`origin`：远程；`main`：分支 | 首次推送并建立跟踪 |
| `git push` | 无参数：推到已跟踪的上游 | 后续推送 |
| `git pull --rebase` | `--rebase`：把本地提交重放到远程之后 | 拉取并保持线性历史 |

> 记忆方法：`-c` 常见于 create，`-d` 常见于 delete，`-m` 常见于 message/move（看命令语境），`-u` 是 set-upstream，`-v` 是 verbose，`-a`/`-A` 是 all。

---

### 4.5 `.gitignore`：哪些文件不该进 Git

有些文件不应该提交：

- 虚拟环境 `.venv/`
- Python 缓存 `__pycache__/`、`*.pyc`
- 数据文件/模型权重（体积大）
- 密钥 `.env`、`*.pem`
- 编辑器配置 `.vscode/`（可选）

在仓库根目录创建 `.gitignore`：

```gitignore
# 匹配所有名为 __pycache__ 的目录
# 末尾的 / 表示只匹配目录，不匹配同名文件
__pycache__/

# * 匹配任意字符；[cod] 匹配 c、o、d 中的任意一个
# 所以能匹配 .pyc / .pyo / .pyd
*.py[cod]

# 匹配 .venv/ 和 venv/ 目录
.venv/
venv/

# 测试缓存
.pytest_cache/
.coverage

# 编辑器
.vscode/
.idea/

# 临时文件
*.tmp
*.log

# 只忽略 data/ 下的 .tmp 文件
data/*.tmp

# 密钥/证书：绝对不要提交
.env
*.pem
```

`.gitignore` 的规则：

- 只对“尚未被 Git 跟踪”的文件生效。
- 已经被跟踪的文件，即使写进 `.gitignore`，仍然会被继续跟踪；必须先 `git rm --cached`。
- `#` 开头是注释；`!` 开头表示取反（例外）。

已经不小心 `git add` 了怎么办：

```bash
# git rm：从 Git 中移除文件
# --cached：只从索引/暂存区移除，保留工作区文件
# .env：目标文件
git rm --cached .env

# 如果整个目录已经提交过，先加到 .gitignore，再移除跟踪
# -r：recursive，递归处理目录下所有文件
# --cached：只删索引记录，不删磁盘文件
git rm -r --cached .venv

# 提交这次“停止跟踪”的改动
git commit -m "chore: stop tracking .venv"
```

---

### 4.6 在真实学习仓库里初始化 Git

练习完 `git-practice/` 后，回到 `/root/aiinfra`，把整个学习仓库纳入 Git。

> 如果 `/root/aiinfra` 已经是 Git 仓库（`git status` 能输出 `On branch main`），跳过 `git init`，直接看 4.7。

```bash
# cd：切换到学习仓库根目录
cd /root/aiinfra

# git init：创建仓库
# -b main：初始分支名为 main（-b = --initial-branch）
# 如果 Git 版本低于 2.28：
#   git init
#   git branch -m main   # -m = --move，把当前分支重命名为 main
git init -b main

# git status：先看会提交哪些东西
# 确认没有 .venv/、密钥、模型权重、大文件
git status

# git add .：把当前目录及子目录的所有未忽略改动加入暂存区
# . 表示当前目录；.gitignore 里的文件会被跳过
git add .

# git commit：生成第一次提交
# -m：提交说明；写清楚这次提交做了什么
git commit -m "chore: 初始化 AI Infra 学习仓库（S0 W1）"

# git log：确认提交成功
# --oneline：一行一个提交
git log --oneline
```

常见错误：

| 现象 | 原因 | 解决 |
|---|---|---|
| `fatal: not a git repository` | 当前目录不是仓库 | `cd` 到仓库根目录，或 `git init -b main` |
| `nothing to commit, working tree clean` | 没有新改动，或文件没保存 | `git status` 确认 |
| `Please tell me who you are` | 没配 `user.name`/`user.email` | 执行 4.2 的两条 `git config` |
| `error: pathspec ... did not match` | 文件名拼错/路径不对 | `ls` 确认文件名 |
| 提交里混进了 `.venv` | `git add .` 前没检查 | `git rm -r --cached .venv`，补 `.gitignore` |

---

### 4.7 把本地仓库推送到 GitHub

下面以 `/root/aiinfra` 这个学习仓库为例。你要先有一个 GitHub 账号。

最短路径（前提：SSH key 已加到 GitHub；详细解释见下面各小节）：

```bash
# origin：远程名；后面换成你的 SSH 地址
git remote add origin git@github.com:<你的用户名>/<仓库名>.git

# -M：强制把当前分支改名为 main
git branch -M main

# -u：建立上游跟踪；origin：远程名；main：本地分支
git push -u origin main
```

#### 4.7.1 在 GitHub 上创建空仓库

1. 打开 GitHub，点右上角 `+` → `New repository`。
2. `Repository name` 填一个名字，例如 `aiinfra-learning`。
3. **不要**勾选 `Add a README file`、`Add .gitignore`、`Choose a license`。
   - 勾选后远程会先有一个提交，本地推送时容易出现 `non-fast-forward` 或 `unrelated histories`。
4. 点 `Create repository`。
5. 复制页面上的 SSH 地址，形如：

   ```text
   git@github.com:<你的用户名>/<仓库名>.git
   ```

#### 4.7.2 配置 GitHub 的 SSH key

```bash
# ssh-keygen：生成 SSH 密钥对
# -t ed25519：密钥类型；ed25519 比 RSA 更短、更安全
# -C "your_email@example.com"：给公钥加注释，方便在 GitHub 上辨认
# 交互提示里直接回车用默认路径；建议设置 passphrase
ssh-keygen -t ed25519 -C "your_email@example.com"

# cat：打印公钥内容
# ~/.ssh/id_ed25519.pub：公钥文件；.pub 结尾才是公钥
# 私钥是 ~/.ssh/id_ed25519（没有 .pub），绝对不能发给别人
cat ~/.ssh/id_ed25519.pub
```

如果这台机器已经有 `~/.ssh/id_ed25519`，直接复用它，**不要覆盖**。也可以给 GitHub 单独生成一个：

```bash
# -f ~/.ssh/id_ed25519_github：file，指定私钥输出路径
#   对应的公钥会自动生成在 ~/.ssh/id_ed25519_github.pub
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519_github
```

复制输出的整行公钥，然后：

1. GitHub 右上角头像 → `Settings`。
2. 左侧 `SSH and GPG keys` → `New SSH key`。
3. `Title` 随便写，例如 `aiinfra-server`；`Key type` 选 `Authentication Key`。
4. 粘贴公钥，点 `Add SSH key`。

测试：

```bash
# ssh：SSH 客户端
# -T：不分配伪终端（test only）；GitHub 只用来验证认证，不需要交互 shell
# git@github.com：GitHub 的 SSH 地址，用户名固定是 git
ssh -T git@github.com
```

成功时会看到：

```text
Hi <你的用户名>! You've successfully authenticated, but GitHub does not provide shell access.
```

如果 22 端口被网络阻断，可以改用 443 端口：

```bash
# -p 443：连接 443 端口（HTTPS 端口），绕过对 22 端口的封锁
# git@ssh.github.com：GitHub 提供的 443 端口 SSH 入口
ssh -T -p 443 git@ssh.github.com
```

如果这样能成功，在 `~/.ssh/config` 里加：

```sshconfig
Host github.com
    HostName ssh.github.com   # 实际连接的域名
    Port 443                  # 实际连接的端口
    User git                  # GitHub SSH 用户名固定是 git
```

#### 4.7.3 关联远程仓库

```bash
# 回到学习仓库根目录
cd /root/aiinfra

# git remote：管理远程仓库
# add：新增一个远程
# origin：远程的名字，Git 约定俗成的默认名（可以改，但没必要）
# git@github.com:<用户名>/<仓库名>.git：SSH 形式的远程地址
git remote add origin git@github.com:<你的用户名>/<仓库名>.git

# -v：verbose，显示 fetch（拉取）和 push（推送）两个 URL
git remote -v
```

如果提示 `remote origin already exists`：

```bash
# set-url：修改已有远程的 URL，而不是重复添加
git remote set-url origin git@github.com:<你的用户名>/<仓库名>.git
```

#### 4.7.4 确认分支名

```bash
# --show-current：只输出当前分支名
git branch --show-current

# 如果输出不是 main，把当前分支强制重命名为 main
# -M：--move --force，强制重命名（会覆盖同名分支）
#     普通重命名用 -m；这里用 -M 保证一定改成 main
git branch -M main
```

#### 4.7.5 首次推送

```bash
# git push：把本地提交上传到远程
# -u：--set-upstream，把本地 main 和远程 origin/main 关联起来
#     以后直接 git push / git pull 就知道默认推/拉到哪
# origin：远程名
# main：本地分支名
git push -u origin main
```

成功后：

- GitHub 仓库页面能看到你的文件和提交。
- 本地执行 `git status` 会显示 `Your branch is up to date with 'origin/main'`。
- `git branch -vv` 会显示本地 `main` 跟踪 `origin/main`。
  - `-vv`：比 `-v` 更详细，第二个 `v` 会显示上游跟踪关系。

#### 4.7.6 以后的日常提交流程

```bash
# 1. 看改了什么
git status

# 2. 把要提交的文件加入暂存区
# <file> 换成实际文件名；git add . 表示当前目录全部
git add <file>

# 3. 提交
# -m：提交说明
git commit -m "feat: ..."

# 4. 推送到 GitHub
# 因为前面用了 -u，这里不需要再写 origin main
git push
```

如果远程有你本地没有的提交（例如你在网页上改过 README）：

```bash
# git pull：fetch + 整合远程更新
# --rebase：把本地提交“重放”到远程最新提交之后
#           好处是历史保持一条直线，不产生多余的 merge commit
git pull --rebase

# 如果 rebase 有冲突：
#   解决冲突 -> git add <file> -> git rebase --continue
#   --continue：继续执行被冲突暂停的 rebase
# 想放弃这次 rebase：
#   git rebase --abort
#   --abort：中止 rebase，恢复到 rebase 前

git push
```

#### 4.7.7 常见错误

| 现象 | 原因 | 解决 |
|---|---|---|
| `remote origin already exists` | 已经添加过 `origin` | `git remote set-url origin <新地址>` |
| `Permission denied (publickey)` | 公钥没加到 GitHub，或用的 key 不对 | `ssh -T git@github.com` 测试；重新添加公钥；`ssh-add ~/.ssh/id_ed25519`（把私钥加入 ssh-agent 缓存） |
| `Support for password authentication was removed` | 用账号密码走 HTTPS | 改用 SSH；或生成 Personal Access Token 当密码 |
| `Updates were rejected because the remote contains work...` | 远程有你本地没有的提交 | `git pull --rebase origin main`，解决冲突后再 `git push` |
| `src refspec main does not match any` | 本地没有 `main` 分支或没有提交 | `git branch -M main`；确认 `git log --oneline` 有提交 |
| `fatal: refusing to merge unrelated histories` | 远程仓库初始化时带了 README/提交 | 新建空仓库重来；或 `git pull --allow-unrelated-histories`（允许合并无关历史） |
| `Could not read from remote repository` | 远程地址错，或没有权限 | `git remote -v` 检查 URL；确认仓库属于你 |
| `Host key verification failed` | 服务器重装/网络中间人，known_hosts 里旧指纹不匹配 | 核对 GitHub 指纹后 `ssh-keygen -R github.com` 删除旧记录 |
| `! [rejected] main -> main (fetch first)` | 远程比本地新 | 先 `git pull --rebase`，再 `git push` |

#### 4.7.8 HTTPS 方式（可选）

如果你暂时不想配 SSH，也可以用 HTTPS：

```bash
# https://github.com/<用户名>/<仓库名>.git：HTTPS 形式的远程地址
git remote add origin https://github.com/<用户名>/<仓库名>.git

# GitHub 不再接受账号密码
# 密码位置填 Personal Access Token（PAT）
# 生成路径：GitHub Settings -> Developer settings -> Personal access tokens
# 权限至少勾选 repo；token 只显示一次，别写进代码/命令历史
git push -u origin main
```

> 推送前最后检查一遍：`git status` 里不要有 `.env`、私钥、模型权重、`.venv/`。这些东西一旦推到 GitHub，即使删除也可能留在历史里。

---

## 5. Python 类入门

> 今天只建立第一印象；Day 2 会系统讲继承、组合、property、魔术方法。

### 5.1 为什么需要类

假设你要记录很多次模型实验，每次都有名字、模型、学习率、batch size、准确率：

**用字典：**

```python
# 用字典记录一条实验
exp = {
    "name": "qwen-lr1e-4",       # 实验名
    "model": "Qwen2.5-7B",       # 模型名
    "lr": 0.0001,                # 学习率
    "batch_size": 8,             # 批大小
    "accuracy": 0.923,           # 准确率
}

# 想算一个“是否达标”，只能每次手写判断
is_good = exp["accuracy"] >= 0.9
```

问题：

- 字段名靠约定，拼错 `acuracy` 运行时才发现。
- “是否达标”这种逻辑散落在各处。
- 没有统一的校验，`accuracy=1.5` 也能塞进去。
- 想给实验加一个“摘要”方法，无处可放。

**用类：**

```python
class Experiment:
    """一条实验记录；数据和操作数据的方法放在一起。"""

    def __init__(self, name, model, lr, batch_size, accuracy):
        self.name = name
        self.model = model
        self.lr = lr
        self.batch_size = batch_size
        self.accuracy = accuracy

    def is_good(self, threshold=0.9):
        """判断准确率是否达到阈值。"""
        return self.accuracy >= threshold
```

使用：

```python
exp = Experiment("qwen-lr1e-4", "Qwen2.5-7B", 0.0001, 8, 0.923)
print(exp.is_good())   # True
```

类的价值：**把数据和行为绑在一起，并提供一个统一的校验入口。**

### 5.2 最小类

```python
# class 关键字定义一个类；类名用大驼峰（PascalCase）
class ModelConfig:
    """模型配置：演示类、实例、属性、方法。"""

    # 类属性：所有实例共享的一份数据
    # 这里表示默认精度；如果某个实例不单独设置，就会读到这个值
    default_precision = "fp16"

    # __init__ 是构造方法：创建对象时自动调用
    # self 代表“当前这个实例”，由 Python 自动传入，不需要你手动传
    def __init__(self, name, hidden_size, num_layers):
        # 实例属性：每个对象各自一份
        self.name = name                    # 模型名
        self.hidden_size = hidden_size      # 隐藏层维度
        self.num_layers = num_layers        # 层数
        self.precision = self.default_precision  # 从类属性取默认值

    # 实例方法：第一个参数必须是 self
    def describe(self):
        """返回一段人类可读的描述。"""
        return (
            f"ModelConfig(name={self.name}, "
            f"hidden_size={self.hidden_size}, "
            f"num_layers={self.num_layers}, "
            f"precision={self.precision})"
        )

    # 另一个实例方法：用属性做判断
    def is_tiny(self):
        """参数量很小的时候，方便在 2C2G 服务器上做逻辑验证。"""
        return self.hidden_size <= 256 and self.num_layers <= 6
```

创建对象：

```python
# 创建实例：会把参数传给 __init__
config = ModelConfig("tiny-transformer", hidden_size=128, num_layers=4)

# 访问实例属性
print(config.name)            # tiny-transformer
print(config.hidden_size)     # 128

# 访问类属性（通过实例也能访问到）
print(config.default_precision)  # fp16

# 调用实例方法：注意不需要手动传 self
print(config.describe())
print(config.is_tiny())       # True
```

### 5.3 `__init__` 和 `self` 到底在干什么

```python
config = ModelConfig("tiny-transformer", 128, 4)
```

大致等价于：

```text
1. 创建一个空对象
2. 调用 ModelConfig.__init__(新对象, "tiny-transformer", 128, 4)
3. __init__ 里的 self 就是“新对象”
4. 把 name/hidden_size/... 挂到新对象上
5. 返回这个对象，赋值给 config
```

所以：

- `self` 不是关键字，只是约定名；换成 `this` 也能跑，但没人这么写。
- 定义方法时第一个参数必须是 `self`；调用时**不要**传。
- `self.name = name` 左边是实例属性，右边是传进来的参数。
- 如果写成 `name = name`，只是给局部变量赋值，对象上没有这个属性。

### 5.4 实例属性 vs 类属性

```python
class Demo:
    # 类属性：所有实例共享
    category = "experiment"

    def __init__(self, name):
        # 实例属性：每个实例独立
        self.name = name

a = Demo("a")
b = Demo("b")

print(a.category, b.category)  # experiment experiment
print(a.name, b.name)          # a b

# 给 a 单独设置 category：会在 a 上创建一个实例属性，遮蔽类属性
a.category = "custom"
print(a.category)  # custom
print(b.category)  # experiment
print(Demo.category)  # experiment
```

**可变类属性的坑：**

```python
class BadDemo:
    # 危险：列表是可变对象，所有实例共享同一个列表
    items = []

    def add(self, x):
        self.items.append(x)

x = BadDemo()
y = BadDemo()
x.add(1)
print(y.items)  # [1] —— y 也被影响了
```

正确写法：

```python
class GoodDemo:
    def __init__(self):
        # 每个实例创建自己的列表
        self.items = []

    def add(self, x):
        self.items.append(x)
```

### 5.5 方法、`@classmethod`、`@staticmethod` 先认识一下

```python
class Experiment:
    # 类属性：所有实验的默认阈值
    default_threshold = 0.9

    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    # 实例方法：需要访问具体对象（self）
    def is_good(self):
        return self.accuracy >= self.default_threshold

    # 类方法：第一个参数是 cls（类本身），常用来做工厂方法
    @classmethod
    def from_dict(cls, data):
        # 用字典创建对象；Day 4 的 Experiment.from_dict 会用到
        return cls(data["name"], data["accuracy"])

    # 静态方法：既不访问 self，也不访问 cls，只是放在类里的普通函数
    @staticmethod
    def format_accuracy(value):
        # 把 0.923 格式化成 "92.3%"
        return f"{value * 100:.1f}%"
```

使用：

```python
exp = Experiment.from_dict({"name": "demo", "accuracy": 0.923})
print(exp.name)                        # demo
print(exp.is_good())                   # True
print(Experiment.format_accuracy(0.923))  # 92.3%
```

今天先知道有这三种方法；Day 2 会讲各自适用场景。

### 5.6 跑今天的示例文件

```bash
cd /root/aiinfra/S0-foundation/W1-environment-and-python

# 直接运行示例
python3 examples/day1_class_basics.py
```

示例文件里有一个 `ModelConfig` 类，包含：

- `__init__` 和 `self`
- 实例属性 / 类属性
- `describe()` / `is_tiny()` 方法
- `__repr__` 的预览
- 一个 `if __name__ == "__main__":` 的测试区

先跑一遍，再打开文件逐行读。读完后做下面的练习。

### 5.7 今日 OOP 练习

在 `examples/day1_class_basics.py` 里加一个类 `DatasetConfig`：

```python
# 要求：
# 1. __init__ 接收 name、num_samples、seq_len
# 2. 实例属性保存这三个值
# 3. 方法 total_tokens() 返回 num_samples * seq_len
# 4. 方法 describe() 返回一段描述
# 5. 创建两个对象，打印它们的 total_tokens()
```

参考答案（先自己写，再看）：

```python
class DatasetConfig:
    """数据集配置：练习类、属性、方法。"""

    def __init__(self, name, num_samples, seq_len):
        self.name = name                # 数据集名
        self.num_samples = num_samples  # 样本数
        self.seq_len = seq_len          # 每条样本的 token 长度

    def total_tokens(self):
        """总 token 数 = 样本数 × 每条长度。"""
        return self.num_samples * self.seq_len

    def describe(self):
        return (
            f"DatasetConfig(name={self.name}, "
            f"num_samples={self.num_samples}, seq_len={self.seq_len}, "
            f"total_tokens={self.total_tokens()})"
        )
```

---

## 6. 今日复盘（1 小时）

### 6.1 写笔记

打开 `notes/2026-11-16.md`，在“待我填写的笔记”里写三行：

```text
今天产出：
今天卡点：
明天第一件事：
```

### 6.2 自查

- [ ] `ssh aiinfra` 不输密码能登录
- [ ] tmux 分离后 `tmux ls` 能看到会话，重连后任务还在
- [ ] `git log --oneline` 至少有一条自己的提交
- [ ] `python3 examples/day1_class_basics.py` 能跑通
- [ ] 能不看代码，口述 `__init__`、`self`、实例属性的作用

---

## 7. 明日预告

Day 2 会把今天的类“拆开揉碎”：

- `__repr__` / `__str__` / `__eq__` 到底什么时候被调用
- 继承：`class A(B)` 和 `super().__init__`
- 组合：一个类持有另一个类，为什么项目里更常用组合
- `@property`、`@classmethod`、`@staticmethod`
- Git 分支、合并冲突、`restore` / `reset` / `revert` 的区别

---

## 8. 延伸阅读（可选，不超过 20 分钟）

- [MIT Missing Semester · Shell](https://missing.csail.mit.edu/2020/course-shell/)
- [MIT Missing Semester · Command-line Environment](https://missing.csail.mit.edu/2020/command-line/)
- [Pro Git 中文版 · 起步](https://git-scm.com/book/zh/v2)
- [tmux 入门](https://github.com/tmux/tmux/wiki/Getting-Started)

> 今天不要打开 vLLM / PyTorch / CUDA 的任何教程。主线只有环境 + Python 基础。

---

## 9. 复盘问答

> 这些问题来自今天的自查项和常见卡点。先自己回答，再看解析；答不上来就回到对应小节重读。

### Q1. 为什么把公钥放到服务器，就能免密登录？私钥不是一直在本地吗？

SSH 公钥认证不是“把密码换成一个钥匙文件”，而是**签名验证**：

1. 客户端告诉服务器：我想用某个公钥登录。
2. 服务器检查这个公钥是否在 `~/.ssh/authorized_keys` 里。
3. 服务器发一段随机 challenge。
4. 客户端用**私钥**对 challenge 签名。
5. 服务器用**公钥**验证签名。

私钥从头到尾不离开你的本地电脑；服务器只拿到公钥和签名。签名每次都不一样，所以抓包也无法重放。

```bash
# -v：verbose，打印认证过程
# 如果看到 Authentications that can continue: publickey
# 以及最后的 Authentication succeeded (publickey)，说明走的是公钥认证
ssh -v aiinfra
```

权限为什么重要：

- `~/.ssh` 必须是 `700`：如果组/其他人能写，别人可以往 `authorized_keys` 里加自己的公钥。
- `authorized_keys` 必须是 `600`：防止别人篡改。
- 私钥必须是 `600`：防止别人读走。

### Q2. SSH 连不上，怎么系统排查，而不是乱试？

按网络分层排查，从下往上：

```bash
# 1. 网络层：能不能到服务器
# -c 4：count，只发 4 个 ICMP 包
ping -c 4 1.2.3.4

# 2. 端口层：22 端口是否开放
# -v：verbose；-z：只扫描，不发送数据
nc -vz 1.2.3.4 22

# 3. SSH 服务层：服务器上 SSH 是否在跑
# systemctl status：查看服务状态
systemctl status ssh

# 4. 认证层：看 SSH 握手和认证细节
# -vvv：比 -v 更详细，输出每一轮协商
ssh -vvv aiinfra

# 5. 指定私钥，排除 key 选错
# -i：identity file，指定私钥文件
ssh -i ~/.ssh/id_ed25519 aiinfra
```

工程习惯：把每一步的**现象**记下来，而不是只记“连不上”。例如：

```text
ping 通、22 端口通、ssh -vvv 显示 publickey 被拒
=> 问题在 authorized_keys 或权限，不在网络
```

### Q3. tmux 和 `nohup`、`&`、systemd 有什么区别？什么时候用哪个？

- `&`：把命令放到后台，但 SSH 断开时进程仍可能收到 SIGHUP 而退出。
- `nohup`：忽略 SIGHUP，适合“一次性后台任务”。

  ```bash
  # nohup：忽略挂断信号
  # > train.log：标准输出覆盖写入日志
  # 2>&1：把标准错误(stderr)合并到标准输出(stdout)
  # &：放到后台
  nohup python train.py > train.log 2>&1 &
  ```

- `tmux`：适合**需要交互、需要回看屏幕、需要多窗口**的长任务，例如调试、压测、训练。
- `systemd`：适合**生产服务**，有开机自启、崩溃重启、日志管理；W1 不需要。

选择：

| 场景 | 工具 |
|---|---|
| 跑一次训练/压测，想随时回去看输出 | tmux |
| 一次性后台脚本，不需要交互 | nohup + `&` |
| 长期服务、要自动重启 | systemd |

### Q4. `git add` 和 `git commit` 为什么要分开？直接 commit 不行吗？

分开是为了**让提交可控**：

- 你可能同时改了三件事：修 bug、加注释、改配置。
- 如果直接全部提交，历史里一次 commit 混了三件事，回滚时很难只回滚其中一个。
- `git add` 让你挑选这次要提交的文件/代码块，`git commit` 再打成快照。

```bash
# -p：patch，交互式选择每个 hunk（代码块）是否暂存
# 适合把一个大改动拆成多个小提交
git add -p exp_tracker/models.py

# -m：message，提供提交说明
git commit -m "feat: validate accuracy range"
```

`git commit -a` 可以跳过 `git add`，但它只包含**已跟踪文件**的改动：

```bash
# -a：--all，自动暂存所有已跟踪文件的修改/删除
# 注意：新建的未跟踪文件不会被包含
git commit -a -m "fix: handle empty notes"
```

工程建议：一次 commit 只做一件事；提交信息写“为什么”，不只写“改了什么”。

### Q5. `git init -b main` 的 `-b` 到底是什么？如果 Git 版本旧怎么办？

- `git init`：创建仓库，生成 `.git/`。
- `-b main`：`-b` 是 `--initial-branch` 的缩写，指定初始分支名为 `main`。
- 不写 `-b` 时，旧版 Git 默认 `master`；较新版本可能提示你配置默认名。

```bash
# 查看 Git 版本
git --version

# 如果版本 >= 2.28，可以直接用
git init -b main

# 如果版本 < 2.28：
git init
# -m：--move，重命名当前分支为 main
git branch -m main

# 也可以一次性配置以后 git init 的默认分支名：
# --global：写入 ~/.gitconfig；init.defaultBranch：配置项；main：值
git config --global init.defaultBranch main
```

### Q6. 第一次 commit 后，怎么确认提交内容是对的？

不要只看 `git log` 的一行说明，至少检查四件事：

```bash
# 1. 当前状态：是否还有未提交/未跟踪文件
git status

# 2. 提交历史：哈希、作者、说明
# --oneline：一行一个提交（短哈希 + 说明）
git log --oneline

# 3. 这次提交改了哪些文件、增删多少行
# --stat：statistics，显示文件级统计
# HEAD：当前提交
git show --stat HEAD

# 4. 当前被 Git 跟踪的文件清单
git ls-files
```

如果想看具体 diff：

```bash
# HEAD~1：上一个提交；HEAD：当前提交
# diff：比较两个提交的内容
git diff HEAD~1 HEAD
```

工程习惯：提交前用 `git diff --staged` 看一遍“这次到底要提交什么”。`--staged` 表示暂存区 vs 上一次提交。

### Q7. 为什么不能提交私钥、`.env`？已经提交了怎么办？

提交后，文件会进入 Git 历史。即使后来删除，历史里仍然能找回；推到 GitHub 后还可能被缓存/索引。正确顺序：

1. **立刻轮换密钥**：把泄露的 token、密码、私钥作废，重新生成。删除文件不能挽回已经泄露的凭据。
2. 停止跟踪：

   ```bash
   # --cached：只从索引删除，保留磁盘文件
   git rm --cached .env

   # -r：recursive，递归处理目录
   # --cached：只删索引，保留 .venv/ 目录
   git rm -r --cached .venv

   # -m：提交说明
   git commit -m "chore: stop tracking secrets"
   ```

3. 写进 `.gitignore`，防止再次加入。
4. 如果已经推到远程且影响严重，需要重写历史（`git filter-repo` 等工具）；这会改变所有 commit 哈希，必须和协作者协调。W1 阶段最好的策略是：**一开始就不要提交**。

检查：

```bash
# 列出被跟踪的文件，筛选敏感后缀
# |：管道，把 git ls-files 的输出作为 grep 的输入
# -E：extended regexp，使用扩展正则
git ls-files | grep -E '\.env|\.pem|id_rsa|id_ed25519'
```

`grep -E` 使用扩展正则；如果没有任何输出，说明当前没有被跟踪的敏感文件。

### Q8. 为什么 `def collect(x, result=[])` 和类属性 `items = []` 都是坑？工程上怎么写？

这是 Python 里最经典的“可变对象共享”问题。根因是：**默认参数在函数定义时求值一次**，类属性也只在类定义时创建一次；所有调用/所有实例共享同一个列表。

错误写法一：可变默认参数

```python
# 错误：result=[] 只在函数定义时创建一次
# 第一次调用返回 [1]，第二次调用会在同一个列表上继续 append
def collect_bad(x, result=[]):
    result.append(x)
    return result


print(collect_bad(1))   # [1]
print(collect_bad(2))   # [1, 2] —— 不是 [2]
```

正确写法：用 `None` 表示“没有传”

```python
# 正确：None 是不可变哨兵，每次调用时再创建新列表
def collect(x, result=None):
    if result is None:
        result = []
    result.append(x)
    return result


print(collect(1))   # [1]
print(collect(2))   # [2]
```

如果写类型标注（W2 会系统讲）：

```python
def collect(x: int, result: list[int] | None = None) -> list[int]:
    # list[int] | None 表示“列表或 None”
    if result is None:
        result = []
    result.append(x)
    return result
```

错误写法二：可变类属性

```python
class BadCounter:
    # 错误：items 是类属性，所有实例共享同一个列表
    items = []

    def add(self, x):
        self.items.append(x)


a = BadCounter()
b = BadCounter()
a.add(1)
print(b.items)   # [1] —— b 也被影响了
```

正确写法：在 `__init__` 里创建实例属性

```python
class GoodCounter:
    def __init__(self):
        # 每个实例创建自己的列表
        self.items = []

    def add(self, x):
        self.items.append(x)


a = GoodCounter()
b = GoodCounter()
a.add(1)
print(a.items)   # [1]
print(b.items)   # [] —— 互不影响
```

什么时候类属性可以用：

- 不可变值，例如 `default_precision = "fp16"`。
- 所有实例确实应该共享的常量/配置。
- 不要用可变容器（list/dict/set）做类属性，除非你明确就是要全局共享。

`dataclass` 的对应写法（W2 会讲）：

```python
from dataclasses import dataclass, field


@dataclass
class Counter:
    # default_factory=list：每次创建实例时调用 list()，得到新列表
    items: list[int] = field(default_factory=list)
```

工程检查：

```python
# 快速验证两个对象是否共享状态
a = GoodCounter()
b = GoodCounter()
a.add(1)
assert b.items == []   # 如果这里失败，说明状态被共享了
```

记忆：

```text
可变默认参数 -> 用 None 哨兵，函数内再创建
可变类属性   -> 放 __init__，每个实例一份
dataclass    -> 用 field(default_factory=list)
```
