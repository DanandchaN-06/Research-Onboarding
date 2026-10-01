# 命令行、终端与 Shell｜基础辨析

> 💡 这是一张基础概念补丁：用于区分终端、Shell、CMD、PowerShell 与 Linux bash。内容来自“服务器基础”笔记中的原折叠说明。

**命令行窗口**是一个统称，不一定是 PowerShell。它指的是显示文字、接收键盘输入的地方。你在里面敲命令，命令由 **Shell** 解释执行。
**终端、Shell、命令行界面要分开。** 终端是窗口，Shell 是执行命令的程序，命令行界面是用文字操作电脑的方式。同一个终端窗口可以运行不同 Shell。Windows 上常见 Shell 是 **CMD** 和 **PowerShell**。
**CMD** 全称命令提示符，程序是 cmd.exe，风格传统，管道传文本，脚本是 .bat 或 .cmd，提示符通常是 C:\\Users\\你\>。
**PowerShell** 是后来推出的现代 Shell，基于 .NET，管道传对象，命令常是动词-名词，比如 Get-ChildItem，也有 dir、cd、ls 等别名，脚本是 .ps1，提示符通常有 PS，比如 PS C:\\Users\\你\>。
**简单说，CMD 老而简单，PowerShell 新而强大。** PowerShell 提示符前面有 PS，这是最明显的区别。

**bash 是 Linux 和 Unix 系统上最常见的一种 Shell。** Shell 可以理解成“命令解释器”，它负责接收你输入的命令，把命令翻译给系统内核执行，再把结果返回给你。
**一、打开 CMD 的方法**
**方法一：** 按 Win+R，输入 cmd，回车。
**方法二：** 开始菜单搜索 cmd。
**方法三：** 文件夹地址栏输入 cmd。
**方法四：** Win+X 菜单选命令提示符或终端。
**方法五：** 搜索后右键，以管理员身份运行。
**二、打开 PowerShell 的方法**
**方法一：** 按 Win+R，输入 powershell，回车。
**方法二：** 开始菜单搜索 powershell。
**方法三：** 文件夹地址栏输入 powershell。
**方法四：** Win+X 菜单选 Windows PowerShell 或终端。
**方法五：** 搜索后右键，以管理员身份运行。
**三、Windows Terminal**
Windows Terminal 是另一个终端程序。按 Win+R，输入 wt，可打开。里面可以新建 PowerShell、CMD、WSL 等。
**四、在 VS Code 里打开终端**
先打开 VS Code。按 **Ctrl + 反引号键**，反引号键通常在 Esc 下面。或者点顶部菜单 **Terminal**，再点 **New Terminal**。或者点 **View**，再点 **Terminal**。也可以用 **Ctrl+Shift+P** 打开命令面板，输入 **Terminal: Create New Terminal**。
打开后下方出现终端面板。VS Code 默认可能是 PowerShell。点终端面板右上角加号旁边的下拉箭头，可以新建 **Command Prompt、PowerShell、Git Bash、WSL** 等。
想改默认终端，按 **Ctrl+Shift+P**，输入 **Terminal: Select Default Profile**，然后选 Command Prompt 或 Windows PowerShell 等。
**Remote-SSH 连上服务器后**，VS Code 里的终端默认是服务器上的 **Linux bash**，不是本地 CMD 或 PowerShell。
VS Code 终端一般继承 VS Code 的权限，不以管理员身份运行。需要管理员权限时，可以用管理员身份打开 VS Code，或者用外部的 CMD、PowerShell 管理员窗口。
**五、判断自己在哪个窗口**
看提示符：
**C:\\Users\\你\>** 是本地 CMD。
**PS C:\\Users\\你\>** 是本地 PowerShell。
**你@你的电脑 \~ %** 是 Mac 本地终端。
**user@server:\~\$** 是服务器 Linux bash。
**(myenv) user@server:\~\$** 是服务器上且激活了 conda 环境。
也可输入 **hostname** 和 **whoami** 确认。hostname 显示当前主机名，whoami 显示当前用户。
**六、在命令行里怎么输入**
光标处直接打字，按回车执行。不要输入提示符本身，比如不要输 C:\\Users\\你\> 或 PS C:\\Users\\你\>。
命令区分大小写，Linux 下尤其明显。输错按 **Backspace** 删除。取消当前命令按 **Ctrl+C**。上箭头找回上一条命令。**Tab** 自动补全文件名或命令。
**七、快捷键**
Windows CMD 和 PowerShell 里，复制可以选中后回车或 Ctrl+C，粘贴可以右键或 Ctrl+V。
VS Code 终端里，复制 **Ctrl+C**，粘贴 **Ctrl+V**。
取消命令都是 **Ctrl+C**。清屏 CMD 用 **cls**，Linux 用 **clear**。上一条命令用上箭头，自动补全用 Tab。
**八、和服务器终端的关系**
本地打开 CMD 或 PowerShell，只是本地命令行。输入 **ssh 用户名@服务器IP** 并登录后，窗口里运行的就是服务器 Linux bash，提示符变成 **user@server:\~\$**。
这时敲的是 Linux 命令，不是 PowerShell 命令。本地终端用来连服务器，服务器终端用来跑代码。**Remote-SSH** 连上服务器后，VS Code 终端默认也是服务器 bash。
**九、总结**
命令行窗口不一定是 PowerShell。CMD 和 PowerShell 是 Windows 上两种常见 Shell。CMD 老而简单，PowerShell 新而强大。
打开方式记 **Win+R 输入 cmd 或 powershell**。VS Code 里用 **Ctrl + 反引号键** 打开终端，也能切换 CMD、PowerShell 或远程服务器 bash。
看提示符判断自己在 CMD、PowerShell 还是服务器 Linux bash。本地终端用来连接服务器，服务器终端用来运行代码和 conda 命令。
