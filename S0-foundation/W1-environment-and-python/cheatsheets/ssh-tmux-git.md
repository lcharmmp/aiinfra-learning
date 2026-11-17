# SSH / tmux / Git 一页纸

> 每个命令都标出参数含义；不要只记结论。

---

## SSH

### 生成密钥

```bash
# ssh-keygen：生成 SSH 密钥对
# -t ed25519：密钥类型；ed25519 比 RSA 更短、更安全
# -C "aiinfra-w1"：给公钥加注释，方便辨认
ssh-keygen -t ed25519 -C "aiinfra-w1"

# 默认私钥：~/.ssh/id_ed25519（没有 .pub，绝对不外发）
# 默认公钥：~/.ssh/id_ed25519.pub（可以给服务器/GitHub）
```

### 复制公钥到服务器

```bash
# ssh-copy-id：把公钥追加到远程用户的 ~/.ssh/authorized_keys
# -i ~/.ssh/id_ed25519.pub：指定要复制的公钥文件（-i = identity file）
# root@1.2.3.4：远程用户名@服务器地址
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@1.2.3.4
```

手动方式：

```bash
# mkdir -p：创建目录；-p 表示父目录不存在时逐级创建，已存在不报错
mkdir -p ~/.ssh

# chmod 700：所有者可读/写/执行，组和其他人无权限
chmod 700 ~/.ssh

# echo '...'：输出公钥内容
# >> ~/.ssh/authorized_keys：追加写入（> 会覆盖，绝对不要用）
echo 'ssh-ed25519 AAAA... your-comment' >> ~/.ssh/authorized_keys

# chmod 600：所有者可读/写，组和其他人无权限
chmod 600 ~/.ssh/authorized_keys
```

### 配置别名 `~/.ssh/config`

```sshconfig
Host aiinfra                 # 别名，以后 ssh aiinfra 即可
    HostName 1.2.3.4         # 真实 IP/域名
    User root                # 登录用户名
    Port 22                  # SSH 端口；改过端口这里同步改
    IdentityFile ~/.ssh/id_ed25519   # 私钥路径
    ServerAliveInterval 60   # 每 60 秒发一次心跳
    ServerAliveCountMax 3    # 连续 3 次心跳失败才断开
```

```bash
# chmod 600：配置文件含路径信息，限制权限
chmod 600 ~/.ssh/config

# ssh aiinfra：使用别名登录
ssh aiinfra
```

### 验证/排错

```bash
# -v：verbose，打印详细握手过程
ssh -v aiinfra

# -R：remove，删除 known_hosts 中该主机的旧指纹
ssh-keygen -R 1.2.3.4

# -T：不分配伪终端，只测试认证（GitHub 常用）
ssh -T git@github.com

# 权限修正
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/authorized_keys
```

| 错误 | 原因 | 解决 |
|---|---|---|
| `Permission denied (publickey)` | 公钥/权限/用户名不对 | 检查 `authorized_keys`、`chmod` |
| `Connection refused` | SSH 没开/端口错 | `systemctl status ssh`，查端口 |
| `Connection timed out` | 网络/安全组 | 检查安全组和 IP |
| `UNPROTECTED PRIVATE KEY FILE` | 私钥权限太宽 | `chmod 600` |
| `Host key verification failed` | 旧指纹 | 确认后 `ssh-keygen -R` |

**安全：** 私钥永不外发；给私钥设 passphrase；服务器先确认密钥登录成功再禁用密码登录。

---

## tmux

前缀键：`Ctrl+b`，松开后再按功能键。

### 会话

```bash
# tmux new：新建会话
# -s w1：session name，会话名为 w1
tmux new -s w1

# tmux ls：list sessions，列出所有会话
tmux ls

# tmux attach：连接会话
# -t w1：target session，目标会话名
tmux attach -t w1

# tmux kill-session：结束会话
# -t w1：目标会话名；里面的进程也会结束
tmux kill-session -t w1

# -d：detached，创建后不立即连接（后台创建）
tmux new -d -s w1
```

分离：`Ctrl+b` 然后 `d`。

### 窗口

| 操作 | 按键 | 参数/含义 |
|---|---|---|
| 新建 | `Ctrl+b` `c` | create，新建窗口 |
| 重命名 | `Ctrl+b` `,` | 给当前窗口改名 |
| 下一个/上一个 | `Ctrl+b` `n` / `p` | next / previous |
| 列表 | `Ctrl+b` `w` | window list |
| 关闭 | `Ctrl+b` `&` | 关闭当前窗口（会确认） |

### 窗格

| 操作 | 按键 | 参数/含义 |
|---|---|---|
| 垂直分屏 | `Ctrl+b` `%` | 左右分 |
| 水平分屏 | `Ctrl+b` `"` | 上下分 |
| 切换 | `Ctrl+b` 方向键 | 在窗格间移动 |
| 最大化/还原 | `Ctrl+b` `z` | zoom |
| 关闭 | `Ctrl+b` `x` | 关闭当前窗格 |
| 翻页 | `Ctrl+b` `[`，`q` 退出 | copy mode |

### 常见问题

- `no server running`：没有会话，`tmux new -s w1`。
- `sessions should be nested with care`：已在 tmux 里，先 `unset TMUX`。
- 前缀没反应：先按住 Ctrl 再按 b，松开后再按功能键。

---

## Git

### 配置

```bash
# git config：读写配置
# --global：写入 ~/.gitconfig，对所有仓库生效；不加则只对当前仓库生效
# user.name：配置项；"Your Name"：值
git config --global user.name "Your Name"

# user.email：提交记录里的邮箱
git config --global user.email "you@example.com"

# --list：列出所有配置
git config --global --list

# init.defaultBranch：设置以后 git init 的默认分支名
git config --global init.defaultBranch main
```

### 初始化与日常

```bash
# git init：创建仓库（生成 .git/）
# -b main：初始分支名为 main（-b = --initial-branch，Git 2.28+）
# 旧版：git init && git branch -m main
git init -b main

# git status：看分支、暂存区、未暂存、未跟踪文件
git status

# git diff：工作区 vs 暂存区
git diff

# git diff --staged：暂存区 vs 上次提交（--staged = --cached）
git diff --staged

# git add：加入暂存区
# file.py：目标文件；.：当前目录全部
git add file.py
git add .

# git commit：提交暂存区
# -m "..."：直接给提交说明；不加 -m 会打开编辑器
git commit -m "feat: ..."

# git log：看历史
# --oneline：一行一个提交；--graph：画分支图；--all：所有分支
git log --oneline --graph --all

# git show：看某次提交详情
# <hash>：提交哈希
git show <hash>
```

### 分支

```bash
# git branch：列本地分支
# -a：含远程分支；-v：显示最后提交
git branch
git branch -a
git branch -v

# git switch：切换分支
git switch main

# git switch -c：新建并切换
# -c = --create
git switch -c feature/x

# git merge：把 feature/x 合并进当前分支
# --no-ff：禁止快进，强制生成 merge commit
git merge feature/x

# git branch -d：删除已合并分支（-d = --delete）
# -D：强制删除未合并分支（会丢提交）
git branch -d feature/x
git branch -D feature/x

# git branch -m：重命名当前分支（-m = --move）
# -M：强制重命名（覆盖同名）
git branch -m new-name
git branch -M main
```

### 撤销

| 命令 | 参数解释 | 作用 | 危险度 |
|---|---|---|---|
| `git restore file` | `restore` 恢复；`file` 目标文件 | 丢弃工作区改动 | 中 |
| `git restore --staged file` | `--staged` 只恢复暂存区 | 取消暂存 | 低 |
| `git reset --soft HEAD~1` | `--soft` 只移 HEAD；`HEAD~1` 上一个提交 | 撤销提交，改动留在暂存区 | 低 |
| `git reset --mixed HEAD~1` | `--mixed` 默认；重置暂存区 | 撤销提交，改动留在工作区 | 中 |
| `git reset --hard HEAD~1` | `--hard` 连工作区一起重置 | 撤销提交并丢弃改动 | **高** |
| `git revert <hash>` | `revert` 生成反向提交 | 安全撤销已推送内容 | 低 |
| `git reflog` | reference log | 找回误删/误 reset 的提交 | — |

`HEAD~1`：当前提交的第一个父提交，也就是上一个提交；`HEAD^` 等价；`HEAD~2` 往上两个。

### 远程

```bash
# -T：不分配伪终端，只测试认证
ssh -T git@github.com

# git remote：管理远程
# add：新增；origin：远程名；后面是 SSH 地址
git remote add origin git@github.com:user/repo.git

# -v：verbose，显示 fetch/push URL
git remote -v

# git push：上传
# -u：--set-upstream，建立本地 main 与远程 origin/main 的跟踪
# origin：远程名；main：本地分支
git push -u origin main

# 以后直接
git push

# git pull：fetch + 整合
# --rebase：把本地提交重放到远程最新提交之后
git pull --rebase

# 修改远程 URL
git remote set-url origin git@github.com:user/new-repo.git

# 推送标签
git push origin v0.1.0
```

### .gitignore

```gitignore
# 末尾 / 表示只匹配目录
__pycache__/

# * 任意字符；[cod] 匹配 c/o/d 任一字符
*.py[cod]

# 虚拟环境目录
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

# 密钥/证书
.env
*.pem
```

```bash
# git rm：从 Git 移除
# --cached：只删索引，保留磁盘文件
# -r：递归处理目录
git rm --cached .env
git rm -r --cached .venv
```

### 提交信息

```text
feat: 新功能
fix: 修 bug
docs: 文档
test: 测试
refactor: 重构（不改行为）
chore: 杂项（环境/依赖/配置）
```

> 每次提交只做一件事；看 `git log` 应能还原你的开发过程。
