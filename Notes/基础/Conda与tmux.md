# Conda 与 tmux

> 🧭 本页负责服务器上的两类核心工具：**Conda 管环境，tmux 管长期会话**。以可直接照做的工作流为主。

## 一、Conda（待补）

- [ ] 创建、激活、查看与删除环境
- [ ] 包安装、环境导出与复现
- [ ] CUDA、PyTorch 与环境检查

## 二、为什么要用 tmux 或 screen

如果直接跑程序：

```bash
python train.py
```

然后关闭 ssh 连接，程序很可能也会被关掉。但训练模型要跑几个小时甚至几天，不能一直开着电脑。
这时候就要用 `tmux` 或 `screen`：在服务器上创建一个「不会因为你断开 ssh 而消失的会话」。

## 三、tmux

### 3.1 创建会话

```bash
tmux new -s train
```

下表回答的是：这条命令各部分分别是什么意思。

| **部分** | **意思** |
| --- | --- |
| `tmux` | 工具名 |
| `new` | 新建 |
| `-s train` | 会话名叫 `train` |

执行后，会进入一个新界面，底部通常有一行状态栏。

### 3.2 在里面跑程序

```bash
$ python train.py
Epoch 1...
Epoch 2...
```

程序开始跑。

### 3.3 分离会话

先按 `Ctrl + b`，松开，再按：

```bash
d
```

你会看到类似：

```bash
[detached (from session train)]
```

这表示你离开了会话，但程序还在后台跑。

### 3.4 查看有哪些会话

```bash
$ tmux ls
train: 1 windows (created Tue Sep 23 10:00:00 2026) [80x24]
```

### 3.5 恢复会话

```bash
$ tmux attach -t train
```

你会回到 `train` 会话，看到之前的输出。

### 3.6 结束会话

在会话里输入：

```bash
exit
```

或者在外面强制结束：

```bash
tmux kill-session -t train
```

### 3.7 tmux 常用快捷键

下表回答的是：tmux 里最常用的快捷键。

| **快捷键** | **作用** |
| --- | --- |
| `Ctrl + b`，再按 `d` | 分离会话 |
| `Ctrl + b`，再按 `c` | 新建窗口 |
| `Ctrl + b`，再按 `n` | 下一个窗口 |
| `Ctrl + b`，再按 `p` | 上一个窗口 |
| `Ctrl + b`，再按 `%` | 垂直分屏 |
| `Ctrl + b`，再按 `"` | 水平分屏 |
| `Ctrl + b`，再按方向键 | 切换窗格 |
| `Ctrl + b`，再按 `x` | 关闭窗格，会确认 |

**注意**：`Ctrl + b` 是前缀键，按完要松开，再按下一个键。

## 四、screen

`screen` 比 `tmux` 更老，但很多服务器也预装了。

### 4.1 创建会话

```bash
screen -S train
```

### 4.2 在里面跑程序

```bash
$ python train.py
Epoch 1...
Epoch 2...
```

### 4.3 分离会话

先按 `Ctrl + a`，松开，再按：

```bash
d
```

你会看到：

```bash
[detached from 12345.train]
```

### 4.4 查看会话

```bash
$ screen -ls
There is a screen on:
        12345.train     (Detached)
1 Socket in /run/screen/S-user.
```

### 4.5 恢复会话

```bash
screen -r train
```

如果有多个同名会话，可能需要写 PID：

```bash
screen -r 12345
```

### 4.6 结束会话

```bash
screen -S train -X quit
```

或者在会话里输入 `exit`。

### 4.7 screen 常用快捷键

下表回答的是：screen 里最常用的快捷键。

| **快捷键** | **作用** |
| --- | --- |
| `Ctrl + a`，再按 `d` | 分离会话 |
| `Ctrl + a`，再按 `c` | 新建窗口 |
| `Ctrl + a`，再按 `n` | 下一个窗口 |
| `Ctrl + a`，再按 `p` | 上一个窗口 |
| `Ctrl + a`，再按 `"` | 列出窗口 |

> 💡 优先用 `tmux`。如果服务器没有，再用 `screen`。

## 五、后台运行简略总结

下表回答的是：tmux 和 screen 的常用操作一一对照。

| **工具** | **创建** | **分离** | **查看** | **恢复** | **结束** |
| --- | --- | --- | --- | --- | --- |
| `tmux` | `tmux new -s train` | `Ctrl+b` 再 `d` | `tmux ls` | `tmux attach -t train` | `tmux kill-session -t train` |
| `screen` | `screen -S train` | `Ctrl+a` 再 `d` | `screen -ls` | `screen -r train` | `screen -S train -X quit` |

## 六、后续补充

- [ ] 一次标准训练任务的完整工作流

---

## 小结

> ✅ **一句话结论**：Conda 管环境、tmux/screen 管不会因断网而中断的会话；训练任务放进 tmux 会话里跑，`Ctrl+b` 再按 `d` 分离，回来用 `tmux attach -t 名字` 恢复；优先用 tmux，服务器没有时才用 screen。
