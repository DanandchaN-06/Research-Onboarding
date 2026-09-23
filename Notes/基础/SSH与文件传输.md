# SSH 与文件传输

> 本页负责**如何连接服务器、如何安全传输文件**。

## 连接前提

连接服务器前，需要准备：

- 服务器 IP 或域名
- SSH 端口
- 用户名
- 密码或私钥

## SSH

SSH（Secure Shell）是一种加密网络协议，可以安全地远程登录服务器、执行命令和传输文件。SSH 默认使用 TCP 22 端口，客户端通常是 `ssh`，服务端是 `sshd`。

### 登录服务器

```bash
ssh 用户名@主机地址
```

例如：

```bash
ssh root@192.168.1.100
ssh -p 2222 root@192.168.1.100
```

<details>
<summary><strong>第一次登录的完整流程</strong></summary>

1. 第一次连接时，终端会询问是否信任服务器：

   ```text
   Are you sure you want to continue connecting (yes/no/[fingerprint])?
   ```

   确认主机信息无误后，输入 `yes`。

2. 随后输入密码：

   ```text
   root@192.168.1.100's password:
   ```

   输入密码时屏幕不会显示字符，这是正常现象。

3. 登录成功后，会看到类似提示符：

   ```text
   root@server:~#
   ```

4. 使用 `exit`、`logout` 或 `Ctrl+D` 退出服务器。

</details>

### 常用 SSH 命令

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `ssh 用户@主机` | 登录服务器 | `ssh root@192.168.1.100` |
| `ssh -p 端口 用户@主机` | 指定端口 | `ssh -p 2222 root@1.2.3.4` |
| `ssh -i 私钥 用户@主机` | 指定私钥 | `ssh -i ~/.ssh/id_ed25519 root@1.2.3.4` |
| `ssh 用户@主机 "命令"` | 远程执行一条命令 | `ssh root@1.2.3.4 "uptime"` |
| `ssh -v 用户@主机` | 显示调试信息 | `ssh -v root@1.2.3.4` |
| `ssh -V` | 查看本地 SSH 版本 | `ssh -V` |

<details>
<summary><strong>使用密钥登录</strong></summary>

### 1. 在本地生成密钥

```bash
ssh-keygen -t ed25519 -C "我的密钥"
```

默认会生成：

- 私钥：`~/.ssh/id_ed25519`
- 公钥：`~/.ssh/id_ed25519.pub`

Windows 通常保存在：

```text
C:\Users\你的用户名\.ssh\
```

### 2. 把公钥传到服务器

macOS、Linux 或 Git Bash：

```bash
ssh-copy-id root@192.168.1.100
ssh-copy-id -p 2222 root@192.168.1.100
```

Windows PowerShell 默认可能没有 `ssh-copy-id`。这时可以把公钥内容追加到服务器的：

```text
~/.ssh/authorized_keys
```

然后在服务器上设置权限：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

> 私钥只保存在自己的电脑上，不要上传、转发或借给别人。

</details>

## 文件传输

| 工具 | 适合场景 | 特点 |
| --- | --- | --- |
| `scp` | 单个文件或小目录 | 简单直接 |
| SFTP | 手动浏览和管理文件 | 交互式操作 |
| `rsync` | 大目录、大量文件、重复同步 | 支持增量和断点续传 |

<details>
<summary><strong>scp：快速复制文件或目录</strong></summary>

- 上传文件：`scp 本地文件 用户名@主机:/远程目录/`
- 下载文件：`scp 用户名@主机:/远程文件 ./本地目录/`
- 上传目录：`scp -r ./dist 用户名@主机:/远程目录/`
- 下载目录：`scp -r 用户名@主机:/远程目录/ ./本地目录/`
- 指定端口：`scp -P 2222 本地文件 用户名@主机:/远程目录/`
- 指定私钥：`scp -i 私钥路径 本地文件 用户名@主机:/远程目录/`

常用参数：

- `-r`：递归复制目录
- `-P`：指定端口，注意是大写
- `-i`：指定私钥
- `-C`：启用压缩
- `-v`：显示调试信息

</details>

<details>
<summary><strong>SFTP：交互式传输文件</strong></summary>

连接服务器：

```bash
sftp 用户名@主机
sftp -P 2222 用户名@主机
```

进入 SFTP 后常用命令：

| 命令 | 作用 |
| --- | --- |
| `pwd` / `lpwd` | 查看远程目录 / 本地目录 |
| `ls` / `lls` | 列出远程文件 / 本地文件 |
| `cd` / `lcd` | 切换远程目录 / 本地目录 |
| `put` / `get` | 上传 / 下载文件 |
| `put -r` / `get -r` | 上传 / 下载目录 |
| `reput` / `reget` | 断点续传 |
| `exit` / `bye` | 退出 SFTP |

</details>

<details>
<summary><strong>rsync：增量同步目录</strong></summary>

上传目录：

```bash
rsync -avzP ./本地目录/ 用户名@主机:/远程目录/
```

下载目录：

```bash
rsync -avzP 用户名@主机:/远程目录/ ./本地目录/
```

指定 SSH 端口和私钥：

```bash
rsync -avzP -e "ssh -i 私钥路径 -p 2222" ./dist/ root@主机:/var/www/html/
```

排除不需要的文件：

```bash
rsync -avzP --exclude='*.log' --exclude='node_modules/' ./dist/ root@主机:/var/www/html/
```

`--delete` 会删除目标端多余文件，使用前先试运行：

```bash
rsync -avzP --delete --dry-run ./dist/ root@主机:/var/www/html/
```

> `./dist/` 表示同步目录里的内容；`./dist` 表示同步 `dist` 目录本身。

</details>

## 简化登录：SSH 配置文件

在本地编辑配置文件：

- macOS / Linux：`~/.ssh/config`
- Windows：`C:\Users\你的用户名\.ssh\config`

写入：

```sshconfig
Host myserver
    HostName 192.168.1.100
    User root
    Port 22
```

以后可以直接登录：

```bash
ssh myserver
```

## 图形化工具

### Xshell 与 Xftp

Xshell 可以保存主机、端口、用户名、密钥和终端设置；Xftp 用于图形化传输文件。

### WinSCP

WinSCP 是 Windows 上常用的图形化文件传输工具。

### VS Code Remote-SSH

Remote-SSH 可以让本地 VS Code 直接编辑远程服务器上的文件，并在远程终端中运行和调试代码。代码实际运行在服务器上，本地 VS Code 负责显示和操作。

## 大量小文件的传输

大量小文件不要逐个传输。可以先打包：

```bash
tar -czvf 打包名.tar.gz 文件夹名/
```

上传完成后，在服务器上解压：

```bash
tar -xzvf 打包名.tar.gz
```
