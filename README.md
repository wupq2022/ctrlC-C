# CtrlC+C 改进版

## 简介

这是一个基于 [@chenluda/CtrlC-C](https://github.com/chenluda/CtrlC-C) 项目的改进版本，主要添加了智能换行处理功能。感谢原作者提供的优秀代码基础。

## 下载与安装

直接下载可执行文件，无需安装Python环境：

[📥 点击下载 CtrlC+C.zip](https://github.com/wupq2022/ctrlC-C/raw/main/dist/CtrlC%2BC.zip)

使用方法：
1. 下载后解压缩zip文件
2. 双击解压出的CtrlC+C.exe运行程序
3. 程序会在系统托盘显示图标
4. 无需安装，可直接使用

> 注意：由于Windows安全机制，首次运行可能会提示"Windows已保护您的电脑"，这是正常现象。点击"更多信息"，然后选择"仍要运行"即可。

## 智能换行功能

与原版单纯去除所有换行不同，我们实现了更智能的换行处理机制：

1. **保留段落分隔**：连续两个或以上的换行符被视为段落分隔，予以保留
2. **保留语义分隔**：以句号、问号、感叹号等标点符号结尾的行后的换行被视为段落分隔，予以保留
3. **去除行内换行**：其他情况的单个换行符（通常是PDF复制产生的行内换行）会被替换为空格

这种智能处理方式使得从PDF复制的文本更加易读，既去除了烦人的行内换行，又保留了原文的段落结构。

## 使用方法

1. 运行应用程序
2. 在PDF中复制文本
3. 按住 Ctrl 键并连续按两次 C 键
4. 文本会被智能处理并存入剪贴板，可直接粘贴使用

## 其他功能

- 系统托盘菜单中可切换智能换行和去除空格功能
- 支持开机自启动
- 自动检测快捷键冲突 