# SSH / tmux / Git 一页纸

---

## SSH

### 生成密钥

```bash
ssh-keygen -t ed25519 -C "aiinfra-w1"
# 默认私钥: ~/.ssh/id_ed25519
# 默认公钥: ~/.ssh/id_ed25519.pub
```

### 复制公钥到服务器

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@1.2.3.4
```

手动方式：

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAA... your-comment' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 配置别名 `~/.ssh/config`

```sshconfig
Host aiinfra
    HostName 1.2.3.4
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

```bash
chmod 600 ~/.ssh/config
ssh aiinfra
```

### 验证/排错

```bash
ssh -v aiinfra                 # 详细握手过程
ssh-keygen -R 1.2.3.4          # 服务器重装后删除旧 host key
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
tmux new -s w1          # 新建会话
tmux ls                 # 列出会话
tmux attach -t w1       # 重连
tmux kill-session -t w1 # 结束会话
```

分离：`Ctrl+b` 然后 `d`。

### 窗口

| 操作 | 按键 |
|---|---|
| 新建 | `Ctrl+b` `c` |
| 重命名 | `Ctrl+b` `,` |
| 下一个/上一个 | `Ctrl+b` `n` / `p` |
| 列表 | `Ctrl+b` `w` |
| 关闭 | `Ctrl+b` `&` |

### 窗格

| 操作 | 按键 |
|---|---|
| 垂直分屏 | `Ctrl+b` `%` |
| 水平分屏 | `Ctrl+b` `"` |
| 切换 | `Ctrl+b` 方向键 |
| 最大化/还原 | `Ctrl+b` `z` |
| 关闭 | `Ctrl+b` `x` |
| 翻页 | `Ctrl+b` `[`，`q` 退出 |

### 常见问题

- `no server running`：没有会话，`tmux new -s w1`。
- `sessions should be nested with care`：已在 tmux 里，先 `unset TMUX`。
- 前缀没反应：先按住 Ctrl 再按 b，松开后再按功能键。

---

## Git

### 配置

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global --list
```

### 日常

```bash
git status                  # 当前状态
git diff                    # 工作区 vs 暂存区
git diff --staged           # 暂存区 vs 上次提交
git add file.py             # 加入暂存区
git add .                   # 当前目录全部加入（先检查！）
git commit -m "feat: ..."   # 提交
git log --oneline --graph --all
git show <hash>             # 看某次提交
```

### 分支

```bash
git branch                  # 列出分支
git switch main             # 切换
git switch -c feature/x     # 新建并切换
git merge feature/x         # 合并到当前分支
git branch -d feature/x     # 删除已合并分支
git branch -D feature/x     # 强制删除未合并分支
```

### 撤销

| 命令 | 作用 | 危险度 |
|---|---|---|
| `git restore file` | 丢弃工作区改动 | 中 |
| `git restore --staged file` | 取消暂存 | 低 |
| `git reset --soft HEAD~1` | 撤销提交，改动留在暂存区 | 低 |
| `git reset --mixed HEAD~1` | 撤销提交，改动留在工作区 | 中 |
| `git reset --hard HEAD~1` | 撤销提交并丢弃改动 | **高** |
| `git revert <hash>` | 生成反向提交，安全撤销已推送内容 | 低 |
| `git reflog` | 找回误删/误 reset 的提交 | — |

### 远程

```bash
ssh -T git@github.com                       # 测试 GitHub SSH
git remote add origin git@github.com:user/repo.git
git remote -v
git push -u origin main
git pull --rebase
git push origin v0.1.0                      # 推送标签
```

### .gitignore

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.vscode/
.idea/
*.tmp
*.log
.env
*.pem
```

```bash
git rm --cached .env          # 停止跟踪但保留文件
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
