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
# ssh-copy-id 会自动把公钥追加到服务器的 ~/.ssh/authorized_keys
# 替换成你的服务器用户名和 IP
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@1.2.3.4
```

第一次会要求输入服务器密码。成功后测试：

```bash
# 这次应该不再问密码，直接登录
ssh root@1.2.3.4
```

如果 `ssh-copy-id` 不存在（Windows 某些环境），手动做：

```bash
# 1) 在本地打印公钥并复制整行
cat ~/.ssh/id_ed25519.pub

# 2) 登录服务器
ssh root@1.2.3.4

# 3) 在服务器上创建目录并追加公钥
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '把刚才复制的整行公钥粘贴到这里' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

注意：

- `>>` 是追加，不要用 `>` 覆盖，否则会把已有的公钥清空。
- `~/.ssh` 权限必须是 `700`，`authorized_keys` 必须是 `600`，否则 SSH 会拒绝使用公钥。
- 如果服务器是云厂商，检查安全组是否放行 22 端口；如果改了 SSH 端口，连接时加 `-p 端口号`。

### 2.5 配置 SSH 别名

每次都敲 `ssh root@1.2.3.4` 很烦。编辑本地文件 `~/.ssh/config`：

```bash
# 创建或打开配置文件
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
# -v 打印详细握手过程；成功时最后会看到 Authentication succeeded (publickey)
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
# 查看 tmux 版本
tmux -V

# 新建一个名为 w1 的会话
tmux new -s w1

# 在会话里运行一个长任务
sleep 300

# 分离：先按 Ctrl+b，松开，再按 d
# 回到普通 shell 后，查看会话列表
tmux ls

# 重新连接 w1
tmux attach -t w1

# 彻底结束 w1（里面的进程也会结束）
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

在服务器执行（只需一次）：

```bash
# 设置提交者名字；建议用真名或常用 ID
git config --global user.name "Your Name"

# 设置提交者邮箱；GitHub 可用 GitHub 提供的 noreply 邮箱
git config --global user.email "you@example.com"

# 查看当前配置
git config --global --list
```

如果提示 `Please tell me who you are`，就是这两项没配。

### 4.3 在练习目录完成第一次提交

我们专门准备了 `git-practice/`，先在这里练，不污染主项目：

```bash
# 进入练习目录
cd /root/aiinfra/S0-foundation/W1-environment-and-python/git-practice

# 初始化仓库，并把默认分支命名为 main
git init -b main

# 查看状态：此时应该提示 README.md 是 untracked
git status

# 创建一个自己的文件
cat > hello.py <<'PY'
# 这是 Git 练习用的最小 Python 文件
# 打印一句话，证明文件内容被正确提交
print("hello, ai infra")
PY

# 再次查看状态
git status

# 把 hello.py 加入暂存区
git add hello.py

# 查看暂存区状态
git status

# 提交，-m 后面是提交说明
git commit -m "feat: add hello.py for git practice"

# 查看提交历史，--oneline 每个提交一行
git log --oneline
```

预期输出类似：

```text
a1b2c3d (HEAD -> main) feat: add hello.py for git practice
```

再练一次修改和差异：

```bash
# 修改文件：把 hello 改成 hello, world
sed -i 's/hello, ai infra/hello, world/' hello.py

# 查看工作区与暂存区的差异
git diff

# 把修改加入暂存区
git add hello.py

# 查看暂存区与上一次提交的差异
git diff --staged

# 提交第二次
git commit -m "docs: update greeting"

# 查看历史
git log --oneline --graph
```

### 4.4 常用命令速查

| 命令 | 作用 |
|---|---|
| `git status` | 当前在哪个分支、哪些文件改了/没跟踪 |
| `git diff` | 工作区 vs 暂存区 |
| `git diff --staged` | 暂存区 vs 上一次提交 |
| `git add <file>` | 把文件加入暂存区 |
| `git add .` | 把当前目录所有改动加入暂存区（注意别把大文件/密钥加进去） |
| `git commit -m "msg"` | 提交 |
| `git log --oneline --graph --all` | 看历史 |
| `git show <hash>` | 看某次提交的具体改动 |
| `git restore <file>` | 丢弃工作区改动（危险，确认后再用） |
| `git rm --cached <file>` | 停止跟踪但保留文件 |
| `git branch` | 查看分支 |
| `git switch <branch>` | 切换分支 |
| `git switch -c <branch>` | 新建并切换分支 |

### 4.5 `.gitignore`

有些文件不应该进 Git：

- 虚拟环境 `.venv/`
- Python 缓存 `__pycache__/`、`*.pyc`
- 数据文件/模型权重（体积大）
- 密钥 `.env`、`*.pem`
- 编辑器配置 `.vscode/`（可选）

在仓库根目录创建 `.gitignore`：

```gitignore
# Python 字节码缓存
__pycache__/
*.py[cod]

# 虚拟环境
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

# 数据与密钥（按需）
data/*.tmp
.env
*.pem
```

已经不小心 `git add` 了怎么办：

```bash
# 从暂存区移除，但保留工作区文件
git rm --cached .env

# 如果整个目录已经提交过，先加到 .gitignore，再移除跟踪
git rm -r --cached .venv
git commit -m "chore: stop tracking .venv"
```

### 4.6 在真实学习仓库里初始化 Git

练习完 `git-practice/` 后，回到 `/root/aiinfra`，把整个学习仓库纳入 Git：

```bash
cd /root/aiinfra

# 初始化仓库
git init -b main

# 先看会提交哪些东西；确认没有 .venv、密钥、大文件
git status

# 添加所有学习材料
git add .

# 第一次提交
git commit -m "chore: 初始化 AI Infra 学习仓库（S0 W1）"

# 确认
git log --oneline
```

> 从今天起，每天结束前提交一次。提交信息写“做了什么”，不要写“update”。

常见错误：

| 现象 | 原因 | 解决 |
|---|---|---|
| `fatal: not a git repository` | 当前目录不是仓库 | `cd` 到仓库根目录，或 `git init` |
| `nothing to commit, working tree clean` | 没有新改动，或忘了保存文件 | `git status` 确认 |
| `Please tell me who you are` | 没配 user.name/email | 执行 4.2 的两条 config |
| `error: pathspec ... did not match` | 文件名拼错/路径不对 | `ls` 确认文件名 |
| 提交里混进了 `.venv` | `git add .` 前没检查 | `git rm -r --cached .venv`，补 `.gitignore` |

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