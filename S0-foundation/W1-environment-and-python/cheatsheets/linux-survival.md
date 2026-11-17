# Linux 生存命令一页纸（W1 够用版）

> W3 会系统讲进程/内存/文件系统；这里只列本周写代码、跑 Git 会用到的命令。
> 每个短选项都标出含义；不确定时先 `man <命令>` 或 `<命令> --help`。

---

## 目录与文件

```bash
# pwd：print working directory，打印当前目录
pwd

# ls：list，列出目录内容
# -l：long，长格式（权限、所有者、大小、时间）
# -a：all，包含以 . 开头的隐藏文件
ls -la

# cd：change directory，切换目录
cd /path/to/dir

# ..：上一级目录
cd ..

# ~：当前用户的家目录
cd ~

# mkdir：make directory，创建目录
# -p：parents，父目录不存在时逐级创建；已存在不报错
mkdir -p a/b/c

# cp：copy，复制文件
cp file1 file2

# -r：recursive，递归复制整个目录
cp -r dir1 dir2

# mv：move，移动或重命名
mv file1 file2

# rm：remove，删除文件（不可恢复）
rm file

# -r：recursive，递归删除目录
rm -r dir

# -f：force，不提示直接删除；-rf 组合非常危险
# rm -rf dir

# touch：创建空文件；文件已存在时更新时间戳
touch file
```

**危险命令：** `rm -rf`、`git reset --hard`、`dd`。执行前先 `pwd` + `ls` 确认位置。

---

## 查看文件

```bash
# cat：concatenate，把文件内容全部输出（适合小文件）
cat file

# less：分页查看
# 空格翻页，b 上一页，/关键词 搜索，q 退出
less file

# head：显示开头
# -n 20：显示前 20 行（-n = number）
head -n 20 file

# tail：显示结尾
# -n 20：显示后 20 行
tail -n 20 file

# -f：follow，实时跟踪文件新增内容；Ctrl+C 退出
tail -f log.txt

# wc：word count
# -l：只统计行数（lines）
wc -l file
```

---

## 搜索

```bash
# grep：在文件里搜索匹配的行
grep "pattern" file

# -r：recursive，递归搜索目录
# -n：line number，显示行号
grep -rn "pattern" .

# find：查找文件
# .：从当前目录开始
# -name "*.py"：按文件名匹配（* 是通配符）
find . -name "*.py"

# -type f：只找普通文件（f = file；目录是 d）
find . -type f -name "*.md"

# which：在 PATH 里查找命令的可执行文件位置
which python3
```

---

## 权限

```bash
# ls -l：长格式查看权限，例如 -rw-r--r--
ls -l file

# chmod：change mode，修改权限
# 600：所有者读(4)+写(2)，组和其他人无权限
chmod 600 file

# 700：所有者读+写+执行，组和其他人无权限
chmod 700 dir

# +x：给所有用户加执行权限
chmod +x script.sh

# stat：显示文件元信息
# -c '%a %n'：自定义格式；%a 八进制权限，%n 文件名
stat -c '%a %n' file
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
# .ssh 目录：700
chmod 700 ~/.ssh

# 私钥：600
chmod 600 ~/.ssh/id_ed25519

# 授权公钥文件：600
chmod 600 ~/.ssh/authorized_keys
```

---

## 进程与资源

```bash
# ps：process status，查看进程
# a：所有用户的进程
# u：以用户友好格式显示
# x：包含没有控制终端的进程
ps aux

# |：管道，把 ps 输出作为 grep 输入
# grep python：筛选包含 python 的行
ps aux | grep python

# top：实时资源监控；q 退出
top

# htop：更友好的 top（可能没装）
htop

# kill：向进程发送信号
# PID：进程号
# 默认发送 SIGTERM(15)，让进程有机会清理
kill PID

# -9：发送 SIGKILL(9)，强制杀死，进程无法清理
kill -9 PID

# free：内存使用
# -h：human-readable，用 GiB/MiB 显示
free -h

# df：disk free，磁盘空间
# -h：human-readable
df -h

# du：disk usage，目录占用
# -s：summary，只显示总计
# -h：human-readable
du -sh dir

# nproc：number of processors，CPU 核数
nproc
```

---

## 网络

```bash
# ping：测试连通性
# -c 4：count，只发 4 个包
ping -c 4 baidu.com

# curl：发 HTTP 请求
# -I：只取响应头（HEAD 请求）
curl -I https://example.com

# -o file.zip：output，把响应体保存到文件
curl -o file.zip https://...

# wget：下载文件（可能没装）
wget https://...

# ssh：远程登录
# user@host：用户名@主机
ssh user@host

# scp：secure copy，远程复制
# -r：递归复制目录
# -P 端口：指定 SSH 端口（注意是大写 P）
scp file user@host:/path/

# 远程 -> 本地；最后的 . 表示当前目录
scp user@host:/path/file .
```

---

## 压缩

```bash
# tar：打包/解包
# -c：create，创建归档
# -z：gzip 压缩
# -f：file，指定归档文件名
tar -czf archive.tar.gz dir/

# -x：extract，解包
# -z：gzip 解压
# -f：指定归档文件
tar -xzf archive.tar.gz

# unzip：解压 zip
unzip file.zip
```

---

## 包管理（Ubuntu/Debian）

```bash
# apt update：更新软件源索引（不升级已安装软件）
sudo apt update

# apt install：安装软件包
sudo apt install tmux

# apt remove：卸载软件包（保留配置文件）
sudo apt remove tmux

# apt list：列出软件包
# --installed：只看已安装
# | grep tmux：筛选包含 tmux 的行
apt list --installed | grep tmux
```

> 没有 sudo 时不要硬装；先问平台管理员，或用虚拟环境/用户级安装。

---

## Python

```bash
# --version：打印版本
python3 --version

# 运行脚本文件
python3 script.py

# python3 -m：把模块当脚本运行（-m = module）
# venv：标准库虚拟环境模块
# .venv：虚拟环境目录
python3 -m venv .venv

# source：在当前 shell 执行脚本
# .venv/bin/activate：激活虚拟环境
source .venv/bin/activate

# deactivate：退出虚拟环境
deactivate

# -m pip：用当前 Python 的 pip 模块
# install -r requirements.txt：安装文件里列出的依赖
python3 -m pip install -r requirements.txt

# -m unittest：运行标准库测试框架
# discover：自动发现测试
# -s tests：从 tests/ 目录开始
# -v：verbose，输出每个用例
python3 -m unittest discover -s tests -v
```

---

## 管道与重定向

```bash
# >：覆盖写入文件（原内容会丢失）
command > file

# >>：追加写入文件
command >> file

# 2>&1：把标准错误(stderr, 2)重定向到标准输出(stdout, 1)
command 2>&1

# |：管道，把左边输出作为右边输入
command | grep xxx

# head -n 20：只看前 20 行
command | head -n 20
```

---

## 本周最常用组合

```bash
# 看项目结构
# find：查找；. 当前目录；-maxdepth 2 最多两层；-type f 只找文件
# | sort：按字典序排序
find . -maxdepth 2 -type f | sort

# 找所有 Python 文件
find . -name "*.py"

# 看 Git 状态
git status

# 跑测试并只看末尾
# 2>&1：把 stderr 合并到 stdout
# | tail -30：只看最后 30 行
python3 -m unittest discover -s tests -v 2>&1 | tail -30

# 看端口占用（后面起服务会用到）
# ss：socket statistics
# -l：listening，只看监听中的
# -t：TCP
# -n：numeric，显示数字端口
# -p：process，显示进程
ss -ltnp | grep 8000
```
