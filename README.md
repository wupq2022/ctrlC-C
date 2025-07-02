# CtrlC+C

一个智能化的剪贴板增强工具，专为解决PDF文本复制问题而设计。

## 功能特点

- **智能处理换行**：自动识别并保留段落间的换行，去除PDF复制产生的行内换行
- **保留语义结构**：保留句子末尾（标点符号后）的换行符，使文本更易读
- **快捷键操作**：按住Ctrl键并连续按两次C键即可激活功能
- **系统托盘运行**：程序在后台运行，不干扰正常工作
- **自定义选项**：提供智能换行处理和去除空格的可选功能
- **开机自启动**：可设置为开机自动启动

## 使用场景

- 复制PDF文档中的文本，无需手动删除多余的换行符
- 提高阅读和编辑从PDF复制文本的效率
- 让复制的文本保持原有段落结构，便于阅读和编辑

## 下载和使用

1. 从[Releases](https://github.com/wupq2022/ctrlcc/releases)页面下载最新的可执行文件
2. 双击运行程序，它将在系统托盘中显示图标
3. 复制PDF中的文本后，按住Ctrl键并连续按两次C键激活功能
4. 右键点击系统托盘图标可以访问设置选项

## 系统要求

- Windows 10或更高版本

## 从源代码构建

如果您想自行构建程序：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖
pip install pyperclip keyboard pystray pillow pywin32

# 运行程序
python ctrlcc.py
```

## 使用PyInstaller打包

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包为单个可执行文件
pyinstaller --onefile --noconsole --add-data "ctrlcc.ico;." --icon=ctrlcc.ico --name="CtrlC+C" ctrlcc.py
```

## 许可证

MIT License

## 作者

[wupq2022](https://github.com/wupq2022) 