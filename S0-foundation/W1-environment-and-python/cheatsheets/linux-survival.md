# Linux 生存命令一页纸（W1 够用版）

> W3 会系统讲进程/内存/文件系统；这里只列本周写代码、跑 Git 会用到的命令。

---

## 目录与文件

```bash
pwd                     # 当前目录
ls -la                  # 列出所有文件（含隐藏文件）
cd /path/to/dir         # 进入目录
cd ..                   # 上一级
cd ~                    # 家目录
mkdir -p a/b/c          # 递归创建目录
cp file1 file2          # 复制文件
cp -r dir1 dir2         # 递归复制目录
mv file1 file2          # 移动/重命名
rm file                 # 删除文件（不可恢复）
rm -r dir               # 递归删除目录（危险）
touch file              # 创建空文件/更新时间戳
```

**危险命令：** `rm -rf`、`git reset --hard`、`dd`。执行前先 `pwd` + `ls` 确认位置。

---

## 查看文件

```bash
cat file                # 全部输出（小文件）
less file               # 分页查看；空格翻页，q 退出
head -n 20 file         # 前 20 行
tail -n 20 file         # 后 20 行
tail -f log.txt         # 实时跟踪日志；Ctrl+C 退出
wc -l file              # 行数
```

---

## 搜索

```bash
grep "pattern" file             # 在文件里搜
grep -rn "pattern" .            # 递归搜索当前目录，显示行号
find . -name "*.py"             # 按文件名找
find . -type f -name "*.md"     # 只找文件
which python3                   # 命令所在路径
```

---

## 权限

```bash
ls -l file              # 查看权限，例如 -rw-r--r--
chmod 600 file          # 所有者可读写；其他人无权限
chmod 700 dir           # 所有者可读写执行
chmod +x script.sh      # 加执行权限
stat -c '%a %n' file    # 用数字显示权限
```

权限数字：

```text
r=4  w=2  x=1
600 = rw-------
644 = rw-r--r--
700 = rwx------
755 = rwxr-xr-x
```

SSH 要求：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/authorized_keys
```

---

## 进程与资源

```bash
ps aux                  # 所有进程
ps aux | grep python    # 找 python 进程
top                     # 实时资源；q 退出
htop                    # 更好看（可能没装）
kill PID                # 正常结束进程
kill -9 PID             # 强制结束（最后手段）
free -h                 # 内存
df -h                   # 磁盘
du -sh dir              # 目录大小
nproc                   # CPU 核数
```

---

## 网络

```bash
ping -c 4 baidu.com     # 连通性
curl -I https://example.com          # 只看响应头
curl -o file.zip https://...         # 下载
wget https://...                     # 下载（可能没装）
ssh user@host                        # 远程登录
scp file user@host:/path/            # 本地 -> 远程
scp user@host:/path/file .           # 远程 -> 本地
```

---

## 压缩

```bash
tar -czf archive.tar.gz dir/         # 压缩
tar -xzf archive.tar.gz              # 解压
unzip file.zip                       # 解压 zip
```

---

## 包管理（Ubuntu/Debian）

```bash
sudo apt update                      # 更新软件源
sudo apt install tmux                # 安装
sudo apt remove tmux                 # 卸载
apt list --installed | grep tmux     # 查已安装
```

> 没有 sudo 时不要硬装；先问平台管理员，或用虚拟环境/用户级安装。

---

## Python

```bash
python3 --version
python3 script.py
python3 -m venv .venv
source .venv/bin/activate
deactivate
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
```

---

## 管道与重定向

```bash
command > file          # 覆盖输出到文件
command >> file         # 追加
command 2>&1            # 把 stderr 合并到 stdout
command | grep xxx      # 管道过滤
command | head -n 20    # 只看前 20 行
```

---

## 本周最常用组合

```bash
# 看项目结构
find . -maxdepth 2 -type f | sort

# 找所有 Python 文件
find . -name "*.py"

# 看 Git 状态
git status

# 跑测试并只看末尾
python3 -m unittest discover -s tests -v 2>&1 | tail -30

# 看端口占用（后面起服务会用到）
ss -ltnp | grep 8000
```
