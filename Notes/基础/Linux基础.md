# Linux 基础

> 本页负责**进入服务器之后的 Linux 操作基础**，重点是路径、文件、进程与资源查看。
# Linux 基础命令
`命令 -参数 目标；举例：`
```text
df -h
```

| **部分** | **意思** |
| --- | --- |
| `df` | 命令名字，表示查看磁盘 |
| `-h` | 参数，表示用人类容易读的方式显示 |
| 没有目标 | 表示查看所有磁盘 |

文件操作都离不开“路径”。

| **符号** | **意思** |
| --- | --- |
| `/` | 根目录，最顶层 |
| `~` | 当前用户的 home 目录 |
| `.` | 当前目录 |
| `..` | 上一级目录 |
| `-` | 上一次所在的目录 |

绝对路径：从 `/` 开始写，比如 `/home/user/project`。
相对路径：从当前位置写，比如 `project/data`。
## A.文件操作
### **0. 理解路径**
### **1. ****`ls`****：列出目录里有什么**
**作用**：看看当前目录或指定目录里有哪些文件和文件夹。
**常用写法**：
```text
ls
ls -l
ls -la
ls -lh
```
**示范**：
bash
```text
$ ls
data  readme.txt  scripts

$ ls -l
total 12
drwxr-xr-x 2 user user 4096 Sep 23 10:00 data
drwxr-xr-x 2 user user 4096 Sep 23 10:00 scripts
-rw-r--r-- 1 user user  123 Sep 23 10:00 readme.txt
```
**输出解释**：
  - `drwxr-xr-x`：权限，`d` 表示目录。
  - `user user`：所属用户和用户组。
  - `4096`：大小。
  - `Sep 23 10:00`：修改时间。
  - `data`、`scripts`、`readme.txt`：文件名。
**常用参数**：

| **参数** | **意思** |
| --- | --- |
| `-l` | 显示详细信息 |
| `-a` | 显示隐藏文件，比如 `.bashrc` |
| `-h` | 大小用 K、M、G 显示，方便看 |

**注意**：`ls` 不会显示隐藏文件，除非加 `-a`。
### **2. ****`cd`****：切换目录**
**作用**：从当前目录进入另一个目录。
**常用写法**：
```text
cd /home/user/project
cd ~
cd ..
cd -
cd ../..
```
**示范**：
```text
$ pwd
/home/user

$ cd project
$ pwd
/home/user/project

$ cd ..
$ pwd
/home/user

$ cd ~
$ pwd
/home/user
```
**解释**：
  - `pwd` 是“我现在在哪”。
  - `cd project`：进入当前目录下的 `project`。
  - `cd ..`：回到上一级。
  - `cd ~`：回到家目录。
  - `cd -`：回到上一次所在目录。
**注意**：`cd` 成功时通常没有任何输出，这是正常的。
### **3. ****`cp`****：复制文件或目录**
**作用**：把文件或目录复制一份。
**常用写法**：
```text
cp a.txt b.txt
cp a.txt /path/to/dir/
cp -r dir1 dir2
cp -i a.txt b.txt
```
**示范**：
```text
$ ls
a.txt

$ cp a.txt b.txt
$ ls
a.txt  b.txt

$ mkdir backup
$ cp a.txt backup/
$ ls backup
a.txt

$ cp -r backup backup2
$ ls
a.txt  b.txt  backup  backup2
```
**解释**：
  - `cp a.txt b.txt`：把 `a.txt` 复制成 `b.txt`。
  - `cp a.txt backup/`：把 `a.txt` 复制到 `backup` 目录里。
  - `cp -r backup backup2`：复制整个目录，必须加 `r`。
  - `mkdir backup` 的意思是：**在当前所在目录下，新建一个名为 ****`backup`**** 的文件夹。**
**注意**：
  - 复制目录必须加 `r`。
  - 如果目标文件已存在，`cp` 会直接覆盖。想安全一点，用 `cp -i`，覆盖前会问你。
### **4. ****`mv`****：移动或重命名**
**作用**：把文件或目录移动到别处，或者改名。
**常用写法**：
```text
mv a.txt b.txt
mv a.txt /path/to/dir/
mv dir1 /path/to/dir/
```
**示范**：
```text
$ ls
a.txt

$ mv a.txt note.txt
$ ls
note.txt

$ mkdir archive
$ mv note.txt archive/
$ ls
archive

$ ls archive
note.txt
```
**解释**：
  - `mv a.txt note.txt`：把 `a.txt` 改名为 `note.txt`。
  - `mv note.txt archive/`：把 `note.txt` 移动到 `archive` 目录。
  - `mv` 是“剪切”，原位置不会保留文件。
**注意**：`mv` 和 `cp` 不一样。`cp` 是复制，原文件还在；`mv` 是移动，原文件没了。
### **5. ****`rm`****：删除文件或目录**
**作用**：删除文件或目录。
**常用写法**：
```text
rm file.txt
rm -r dir
rm -i file.txt
rm -rf dir
```
**示范**：
```text
$ ls
old.txt  temp

$ rm old.txt
$ ls
temp

$ rm -r temp
$ ls
```
**解释**：
  - `rm old.txt`：删除文件。
  - `rm -r temp`：删除目录，必须加 `r`。
  - `rm -rf dir`：强制删除目录，**极度危险**，不要随便用
  - `-i`：interactive，交互式，每个文件删除前都提示确认
**注意**：
  - Linux 删除通常不可恢复。
  - 用 `rm -rf` 之前，一定先 `pwd` 和 `ls` 确认路径。
  - 不要在不确定的目录里用 `rm -rf *`。
---
## **文件操作简略总结**

| **命令** | **作用** | **最常用写法** | **注意** |
| --- | --- | --- | --- |
| `ls` | 列出内容 | `ls -lh` | `-a` 看隐藏文件 |
| `cd` | 切换目录 | `cd ..`、`cd ~` | 成功时无输出 |
| `cp` | 复制 | `cp -r dir1 dir2` | 复制目录要 `-r` |
| `mv` | 移动/改名 | `mv old new` | 原位置不保留 |
| `rm` | 删除 | `rm file`、`rm -r dir` | `rm -rf` 极度危险 |

## B.**查看 CPU / GPU 状态**
### **1. ****`top`****：看 CPU、内存、进程**
**作用**：实时查看服务器 CPU、内存、进程占用情况。
```text
top
```
**输出示范**：
```text
top - 10:00:00 up 1 day,  2 users,  load average: 0.10, 0.20, 0.15
Tasks: 120 total,   1 running, 119 sleeping,   0 stopped,   0 zombie
%Cpu(s):  5.0 us,  1.0 sy,  0.0 ni, 93.0 id,  1.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :  32000.0 total,  20000.0 free,   8000.0 used,   4000.0 buff/cache
MiB Swap:   4096.0 total,   4096.0 free,      0.0 used.  22000.0 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 1234 user      20   0  1000000 500000 100000 R  50.0   1.5   0:10.00 python
 5678 user      20   0   800000 300000  80000 S  10.0   0.9   0:05.00 bash
```
**第一行：系统概况**
```text
top - 10:00:00 up 1 day,  2 users,  load average: 0.10, 0.20, 0.15
```
  - `10:00:00`：当前时间。
  - `up 1 day`：系统已经开机 1 天。
  - `2 users`：当前有 2 个用户登录。
  - `load average: 0.10, 0.20, 0.15`：过去 1 分钟、5 分钟、15 分钟的平均负载。
    - 这个值要和 CPU 核数对比。
    - 比如 8 核机器，负载 0.1 说明非常空闲。
    - 如果负载长期接近或超过核数，说明 CPU 比较忙。
    - 这里三个值都很低，说明服务器很闲。
**第二行：任务统计**
```text
Tasks: 120 total,   1 running, 119 sleeping,   0 stopped,   0 zombie
```
  - `120 total`：当前共有 120 个进程/任务。
  - `1 running`：1 个正在运行。
  - `119 sleeping`：119 个在睡眠，等待事件，正常。
  - `0 stopped`：没有被暂停的进程。
  - `0 zombie`：没有僵尸进程。
    - 僵尸进程是已经结束但父进程没回收的进程。少量通常没事，大量要排查。
**第三行：CPU 使用情况**
```text
%Cpu(s):  5.0 us,  1.0 sy,  0.0 ni, 93.0 id,  1.0 wa,  0.0 hi,  0.0 si,  0.0 st
```
  - `us`：用户态占用 CPU，5%。你跑的程序主要算在这里。
  - `sy`：内核态占用 CPU，1%。
  - `ni`：低优先级进程占用，0%。
  - `id`：空闲 CPU，93%。越高越闲。
  - `wa`：等待 I/O 的时间，1%。硬盘或网络慢时会升高。
  - `hi`：硬中断，0%。
  - `si`：软中断，0%。
  - `st`：被虚拟机偷走的时间，0%。云服务器或虚拟机里才明显。
这里空闲 93%，说明 CPU 很轻松。
**第四行：内存**
```text
MiB Mem :  32000.0 total,  20000.0 free,   8000.0 used,   4000.0 buff/cache
```
  - `total`：总内存约 32 GB。
  - `free`：完全空闲约 20 GB。
  - `used`：已使用约 8 GB。
  - `buff/cache`：约 4 GB 用于缓存。
    - 这部分内存不是浪费，系统需要时可以回收。
    - 所以 `free` 少不一定代表内存不够，重点看 `avail Mem`。
**第五行：交换分区**
```text
MiB Swap:   4096.0 total,   4096.0 free,      0.0 used.  22000.0 avail Mem
```
  - `Swap total`：交换分区总共 4 GB。
  - `free`：完全空闲 4 GB。
  - `used`：已使用 0 GB。
  - `avail Mem`：可用内存约 22 GB。
    - 包括 free 加上可回收的缓存。
    - 这个值比较能反映还能给新程序多少内存。
Swap 没被使用，说明物理内存足够，系统没有因为内存不足而用硬盘顶替。
**进程列表**
```text
 PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
1234 user      20   0  1000000 500000 100000 R  50.0   1.5   0:10.00 python
5678 user      20   0   800000 300000  80000 S  10.0   0.9   0:05.00 bash
```
各列含义：
  - `PID`：进程 ID。
  - `USER`：运行该进程的用户。
  - `PR`：进程优先级。
  - `NI`：nice 值，影响优先级，0 表示默认。
  - `VIRT`：虚拟内存总量，包括申请但未必实际使用的内存。
  - `RES`：常驻内存，进程实际占用的物理内存。
  - `SHR`：共享内存。
  - `S`：进程状态。
    - `R`：正在运行或可运行。
    - `S`：睡眠，等待事件。
    - `D`：不可中断睡眠，通常在等 I/O。
    - `Z`：僵尸。
    - `T`：停止。
  - `%CPU`：CPU 占用百分比。
  - `%MEM`：物理内存占用百分比。
  - `TIME+`：进程累计使用的 CPU 时间。
  - `COMMAND`：命令名。
### **2. ****`nvidia-smi`****：看 GPU 状态**
**作用**：查看显卡型号、显存、利用率、哪些进程在占卡。
```text
nvidia-smi
```
**输出示范**：
```text
+-----------------------------------------------------------------------------+

| NVIDIA-SMI 535.104.05   Driver Version: 535.104.05   CUDA Version: 12.2     |

|-------------------------------+----------------------+----------------------+

| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |

|===============================+======================+======================|

|   0  NVIDIA RTX 3090     Off | 00000000:01:00.0 Off |                  N/A |
| 30%   45C    P0    70W / 350W |   1024MiB / 24576MiB |      0%      Default |

+-------------------------------+----------------------+----------------------+

| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |

|=============================================================================|

|    0   N/A  N/A      1234      C   python                              1000MiB |

+-----------------------------------------------------------------------------+
```
**第一行：驱动和 CUDA 版本**
```text
NVIDIA-SMI 535.104.05   Driver Version: 535.104.05   CUDA Version: 12.2
```
`NVIDIA-SMI 535.104.05` 是当前使用的 nvidia-smi 工具版本。`Driver Version: 535.104.05` 是 NVIDIA 显卡驱动版本。`CUDA Version: 12.2` 表示这个驱动最高支持到 CUDA 12.2 运行时。
注意，这里的 CUDA Version 不是你已经安装的 CUDA Toolkit 版本，也不是 conda 环境里的 cudatoolkit 版本。它只是说驱动能支持到 12.2。你实际用哪个 CUDA，取决于 PyTorch、TensorFlow 或 conda 环境里装的版本。可以用 `nvcc --version` 看系统 CUDA Toolkit，用 `python -c "import torch; print(torch.version.cuda)"` 看 PyTorch 实际使用的 CUDA 版本。驱动向下兼容，所以即使你用的是 CUDA 11.8，只要驱动够新，也能跑。
**GPU 基本信息**
```text
GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC
Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M.
0  NVIDIA RTX 3090     Off | 00000000:01:00.0 Off |                  N/A
```
`GPU 0` 表示这是第 0 号显卡。`NVIDIA RTX 3090` 是显卡型号，属于消费级高端卡，显存 24GB，适合深度学习，但不支持 ECC。`Persistence-M Off` 表示持久模式关闭。持久模式主要用于多进程频繁调用 GPU 时减少驱动加载开销，普通使用关闭也没问题。
`Bus-Id 00000000:01:00.0` 是显卡在 PCI 总线上的地址。`Disp.A Off` 表示这张卡没有用于显示输出，服务器通常不接显示器，所以是 Off。`Volatile Uncorr. ECC` 显示 N/A，是因为 RTX 3090 是 GeForce 消费卡，不支持 ECC 显存纠错，所以这里不可用。
**温度、功耗、性能状态**
```text
30%   45C    P0    70W / 350W
```
`Fan 30%` 表示风扇转速为 30%。`Temp 45C` 表示 GPU 当前温度 45 摄氏度，很低，说明显卡很凉快。`Perf P0` 是性能状态，P0 是最高性能状态，P8 是最低。`Pwr:Usage/Cap 70W / 350W` 表示当前功耗 70 瓦，最大功耗上限 350 瓦。70 瓦属于轻载或空闲状态。
**显存和 GPU 利用率**
```text
1024MiB / 24576MiB |      0%      Default
```
`Memory-Usage 1024MiB / 24576MiB` 表示已用显存约 1GB，总显存 24GB。`24576MiB` 就是 24GB。`GPU-Util 0%` 表示当前 GPU 计算利用率为 0%，也就是说，虽然显存被占了一些，但 GPU 现在没有在执行计算任务。`Compute M. Default` 是计算模式，Default 表示默认模式，通常允许多个进程共享 GPU。如果是 Exclusive Process，则表示独占模式。
**进程列表**
```text
GPU   GI   CI        PID   Type   Process name                  GPU Memory
0     N/A  N/A      1234      C   python                              1000MiB
```
这里列出了正在使用 GPU 的进程。`GPU 0` 表示占用的是 0 号卡。`GI` 和 `CI` 是 MIG 相关的 GPU Instance 和 Compute Instance，显示 N/A 表示没有启用 MIG。`PID 1234` 是进程号。`Type C` 表示这是计算进程，C 是 Compute；如果是图形进程，会显示 G；如果两者都是，会显示 C+G。`Process name python` 表示这个进程是 python。`GPU Memory Usage 1000MiB` 表示这个 python 进程占用了约 1000MB 显存。
注意，上面总显存显示 1024MiB，进程显示 1000MiB，两者差了一点。差值是 CUDA 上下文、驱动和运行时本身的开销，正常现象。
**整体判断**
这台服务器目前有一张 RTX 3090，24GB 显存。当前非常空闲：温度 45 度，功耗 70 瓦，GPU 利用率 0%，只被一个 python 进程占了约 1GB 显存。这个 python 进程虽然占着显存，但当前没有在计算，可能是在等待数据、空闲挂起，或者只是加载了模型但没有实际跑运算。
如果你要跑深度学习训练，这张卡资源充足。RTX 3090 24GB 显存适合大多数中等规模模型，但要注意它不是专业卡，不支持 ECC，多卡并行和长时间高负载时散热和稳定性要留意。
**常用查看命令**
bash
```text
nvidia-smi                          # 查看一次
watch -n 1 nvidia-smi               # 每秒刷新
nvidia-smi -l 1                     # 每秒输出一次
nvidia-smi -q                       # 详细输出
nvidia-smi -i 0                     # 只看 0 号 GPU
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
ps -p 1234 -o pid,user,cmd          # 查看 PID 1234 是谁
```
在代码里指定 GPU，可以用：
bash
```text
CUDA_VISIBLE_DEVICES=0 python train.py
```
多卡服务器上，先看哪张卡空闲，再指定 `CUDA_VISIBLE_DEVICES`，避免和别人抢卡。
**常用快捷键**：

| **按键** | **作用** |
| --- | --- |
| `q` | 退出 `top` |
| `P` | 按 CPU 占用排序 |
| `M` | 按内存占用排序 |
| `1` | 展开每个 CPU 核心 |
| `k` | 终止进程，慎用 |

**注意**：在 `top` 里杀进程也要权限，你只能杀自己的进程。
## **CPU / GPU 简略总结**

| **命令** | **作用** | **常用写法** | **注意** |
| --- | --- | --- | --- |
| `top` | 看 CPU、内存、进程 | `top` | `q` 退出，`P`/`M` 排序 |
| `nvidia-smi` | 看 GPU、显存、进程 | `nvidia-smi` | 只看状态，不杀别人进程 |
| `watch` | 循环刷新 | `watch -n 1 nvidia-smi` | 每秒看一次 GPU |

# 常用快捷键

| **快捷键** | **作用** |
| --- | --- |
| `Tab` | 补全命令和路径 |
| `Ctrl + C` | 中断当前命令 |
| `Ctrl + D` | 退出当前 ssh 会话，相当于 `exit` |
| `Ctrl + Shift + C` | 在 ssh 会话里复制 |
| `Ctrl + Shift + V` | 在 ssh 会话里粘贴 |
| 上下方向键 | 浏览历史命令 |

> 基础常识补充：[基础拾遗（Notion）](https://app.notion.com/p/3e495109422d81d49c5fd6ba2155908e)。这里仅保留引用，不纳入服务器学习主线。
