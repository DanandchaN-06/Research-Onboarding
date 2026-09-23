# SSH 与文件传输

> 本页负责**如何连上服务器、如何安全传文件**
# 连接服务器
## 连接前提
服务器IP、端口号、用户名、密码或密钥
## SSH
SSH（Secure Shell）是一种加密网络协议，用于在不安全网络上安全地远程登录、执行命令、传输文件和建立隧道。它采用客户端—服务器模式，默认使用 TCP 22 端口；客户端常见为 `ssh`，服务端为 `sshd`。SSH 通过密钥交换和加密保证通信机密性与完整性，通过密码、公钥、证书或双因素认证确认身份。常见用途包括远程运维 Linux 服务器、Git 代码推送、SFTP/SCP 文件传输、端口转发、跳板机/堡垒机和自动化部署。相比 Telnet、FTP，SSH 最大特点是全程加密。
### SSH 命令
  1. 登录命令<br>`ssh 用户名@主机地址 `
    1. `例 ssh root@192.168.1.100`
    2. 指定端口：`ssh -p 2222 root@192.168.1.100`
<details>
<summary>执行后一般流程：</summary>

      1. 第一次连接会提示：
```text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
输入 `yes`，回车。
      2. 提示输入密码：
```text
root@192.168.1.100's password:
```
输入密码时**屏幕不会显示任何字符**，这是正常的。输完回车。
      3. 成功后提示符会变成类似：
```text
root@server:~#
```
这时已经在远程服务器里了。
退出：
```text
exit
```
或：
```text
logout
```
也可以按 `Ctrl + D`。
</details>
  2. 常用命令

| **命令** | **作用** | **示例** |
| --- | --- | --- |
| `ssh 用户@主机` | 登录服务器 | `ssh root@192.168.1.100` |
| `ssh -p 端口 用户@主机` | 指定端口登录 | `ssh -p 2222 root@1.2.3.4` |
| `ssh -i 私钥路径 用户@主机` | 指定私钥登录 | `ssh -i ~/.ssh/id_ed25519 root@1.2.3.4` |
| `ssh 用户@主机 "命令"` | 远程执行一条命令 | `ssh root@1.2.3.4 "uptime"` |
| `exit` / `logout` / `Ctrl+D` | 退出远程连接 | `exit` |
| `ssh -v 用户@主机` | 显示调试信息，排查连接问题 | `ssh -v root@1.2.3.4` |
| `ssh -V` | 查看本地 SSH 版本 | `ssh -V` |

<details>
<summary>3.密钥生成与传输</summary>

### **第一步：本地生成密钥**
在你自己电脑的终端输入：
bash
```text
ssh-keygen -t ed25519 -C "我的密钥"
```
一路回车即可。默认生成：
    - 私钥：`~/.ssh/id_ed25519`
    - 公钥：`~/.ssh/id_ed25519.pub`
Windows 下路径通常是：
text
```text
C:\Users\你的用户名\.ssh\
```
### **第二步：把公钥传到服务器**
macOS / Linux / Git Bash：
bash
```text
ssh-copy-id root@192.168.1.100
```
如果端口不是 22：
bash
```text
ssh-copy-id -p 2222 root@192.168.1.100
```
Windows PowerShell 默认可能没有 `ssh-copy-id`，可以手动复制公钥内容，追加到服务器的：
bash
```text
~/.ssh/authorized_keys
```
并设置权限：
bash
```text
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```
之后就可以直接：
bash
```text
ssh root@192.168.1.100
```
</details>
<details>
<summary>**4.传文件：scp 、sftp、 rsync**</summary>

<details>
<summary>**1. scp：快速复制文件/目录**</summary>

      - 定位：基于 SSH，适合快速上传、下载单个文件或小目录。
      - 上传文件：`scp 本地文件 用户名@主机:/远程目录/`
      - 下载文件：`scp 用户名@主机:/远程文件 ./本地目录/`
      - 上传目录：`scp -r ./dist 用户名@主机:/远程目录/`
      - 下载目录：`scp -r 用户名@主机:/远程目录/ ./本地目录/`
      - 指定端口：`scp -P 2222 本地文件 用户名@主机:/远程目录/`
      - 指定私钥：`scp -i 私钥路径 本地文件 用户名@主机:/远程目录/`
      - 常用参数：`r` 递归目录；`P` 端口大写；`i` 私钥；`p` 保留时间权限；`C` 压缩；`v` 调试。
      - 特点：简单直接；大量小文件慢；不擅长增量同步和断点续传。
</details>
<details>
<summary>**2. sftp：交互式传文件**</summary>

      - 定位：命令行版 FTP，底层走 SSH，适合手动浏览、上传、下载。
      - 进入：`sftp 用户名@主机`
      - 指定端口：`sftp -P 2222 用户名@主机`
      - 指定私钥：`sftp -i 私钥路径 用户名@主机`
      - 进入后提示符：`sftp>`
      - 查看目录：`pwd` 看远程；`lpwd` 看本地；`ls` 列远程；`lls` 列本地。
      - 切换目录：`cd /远程路径`；`lcd D:\本地路径`。
      - 上传：`put 文件`；`put -r 目录`；`mput *.txt` 上传多个。
      - 下载：`get 文件`；`get -r 目录`；`mget *.log` 下载多个。
      - 断点续传：`reget` 下载续传；`reput` 上传续传。
      - 其他：`mkdir` 建远程目录；`rm` 删除远程文件；`rename` 重命名；`exit`、`bye`、`quit` 退出。
      - 示例流程：`sftp -P 2222 root@192.168.1.100`；`lcd D:\backup`；`cd /var/log`；`get -r nginx`；`put -r D:\site\dist /var/www/html`；`bye`。
      - 特点：适合交互式管理文件；批量同步不如 `rsync`。
</details>
<details>
<summary>**3. rsync：目录同步/增量传输**</summary>

      - 定位：最推荐用于目录同步、大量文件、断点续传、增量传输。
      - 上传：`rsync -avzP ./本地目录/ 用户名@主机:/远程目录/`
      - 下载：`rsync -avzP 用户名@主机:/远程目录/ ./本地目录/`
      - 指定端口和密钥：`rsync -avzP -e "ssh -i 私钥路径 -p 2222" ./dist/ root@主机:/var/www/html/`
      - 排除文件：`rsync -avzP --exclude='*.log' --exclude='node_modules/' ./dist/ root@主机:/var/www/html/`
      - 删除目标端多余文件：`rsync -avzP --delete ./dist/ root@主机:/var/www/html/`
      - 危险操作先试运行：`rsync -avzP --delete --dry-run ./dist/ root@主机:/var/www/html/`
      - 常用参数：`a` 归档；`v` 显示过程；`z` 压缩；`P` 进度+断点续传；`h` 可读单位；`-delete` 删除多余；`-exclude` 排除；`-dry-run` 试运行；`-bwlimit=1000` 限速 KB/s；`e` 指定 SSH 参数。
      - 尾随斜杠关键：`./dist/` 表示把 `dist` 里面的内容复制过去；`./dist` 表示把 `dist` 目录本身复制过去。
      - 特点：增量、同步、排除、断点续传都强；`-delete` 很危险，先用 `-dry-run`。
</details>
</details>
<details>
<summary>5.简化登录</summary>

## **SSH 配置文件**
在本地创建或编辑：
    - macOS / Linux：`~/.ssh/config`
    - Windows：`C:\Users\你的用户名\.ssh\config`
写入：
text
```text
Host myserver
    HostName 192.168.1.100
    User root
    Port 22
```
以后直接：
bash
```text
ssh myserver
```
</details>
### **Xshell**
图形界面，可以保存会话。主机、端口、用户名、密钥、编码、颜色、日志等都能存下来，下次双击就能连。
**Xftp传文件**
### WINSCP
图形化 ，传文件
### **VS Code Remote-SSH**
**VS Code Remote-SSH 是 Visual Studio Code 的一个官方扩展，它让你能用自己的 VS Code 直接连接并开发远程服务器上的代码，就像在本地一样。** 它的核心价值在于：你不需要在远程服务器上安装图形界面或 VS Code 本身，只需要服务器运行着 SSH 服务，就能把本地的 VS Code 变成一个“遥控器”，所有代码编辑、终端命令、调试运行，都在远程服务器上真实执行。
它解决了一个很实际的问题：本地电脑性能有限，但代码必须在高性能服务器上才能跑。传统方式是本地写代码、用 scp 或 Xftp 上传、再 SSH 登录服务器手动运行，流程割裂。Remote-SSH 把整个流程整合在一个窗口里：左边是远程服务器的文件树，右边是编辑器，底部是服务器终端，调试器直接连服务器的 Python 环境。
# 批量文件的打包与传输
传很多小文件，不要一个一个传。先把它们打包成一个压缩包：
```text
tar -czvf 打包名.tar.gz 文件夹名/

tar	打包工具
-c	创建压缩包
-z	用 gzip 压缩
-v	显示过程
-f	指定文件名
```
传上去之后，再在服务器上解压：
```text
tar -xzvf 打包名.tar.gz
```
