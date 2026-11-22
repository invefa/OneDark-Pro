# IDA Pro配色

One Dark Pro Darker的IDA Pro 9主题。样式由[build/gen.py](build/gen.py)从IDA自带的`dark`主题改写而来：保留它的选择器结构，把颜色映射到One Dark色板。

IDA 9的颜色分两层，都存在这个主题文件里：

| 层 | 载体 | 覆盖范围 |
|---|---|---|
| 界面 | Qt样式表选择器 | 主窗口、停靠窗、菜单、工具栏、标签页、树形控件 |
| 列表 | `CustomIDAMemo`下的`qproperty-line-*` | 反汇编视图的前景与背景，含指令、注释、字符串、数字、交叉引用、光标 |

## 一、安装

把整个`onedark-pro-darker`文件夹放进IDA的用户主题目录：

```text
%APPDATA%\Hex-Rays\IDA Pro\themes\onedark-pro-darker\theme.css
%APPDATA%\Hex-Rays\IDA Pro\themes\onedark-pro-darker\icons\
```

重启IDA，打开`Options - Colors`，在`Theme`里选`onedark-pro-darker`。

恢复原样就在同一个下拉里选回`dark`或`default`，主题文件留着不影响。

## 二、两种版本

| 主题 | 范围 | 用途 |
|---|---|---|
| `onedark-pro-darker` | 界面与反汇编视图 | 整套深色，界面与编辑器一致 |
| `onedark-pro-darker-listing` | 只改反汇编视图 | 界面沿用IDA自带的`dark`主题，只有代码区换成One Dark配色 |

两个文件夹都放进主题目录，在`Options - Colors - Theme`里切换。第二个版本把IDA自带的`dark`主题整份嵌进来，末尾追加我们的`CustomIDAMemo`块覆盖列表配色。没有用`@importtheme "dark"`，因为按名字引用跨不过用户主题目录与安装目录，界面会退回浅色默认。

## 三、颜色对应

| 用途 | 取值 | 说明 |
|---|---|---|
| 窗口底 | `#23272e` | 与编辑器一致 |
| 面板与停靠窗 | `#1e2227` | 比窗口暗一档 |
| 浮起层 | `#2c313c` | 按钮、输入框、标题栏 |
| 边框 | `#3e4452` | |
| 正文 | `#abb2bf` | |
| 次要文字 | `#9da5b4` / `#6b717d` | |
| 强调 | `#4d78cc` / `#61afef` | 悬停与焦点 |
| 光标 | `#528bff` | |

反汇编视图沿用语法色：指令`#abb2bf`、注释`#7f848e`、字符串与字符常量`#98c379`、数字`#d19a66`、函数名与代码引用`#61afef`、寄存器`#56b6c2`、关键字与宏`#c678dd`、局部变量与错误`#e06c75`、数据名与段名`#e5c07b`。

生成脚本对没有显式指定的颜色按亮度映射到色板的灰阶，所以整份文件只出现17个色值。

## 四、边界

- 主题只影响IDA自身的界面。反编译器（Hex-Rays）的伪代码配色在`Options - Colors - Decompiler`里，是另一套设置；本轮没有覆盖。
- 图形视图的节点底色按亮度映射到色板的灰阶与语法色，没有逐项调校。
- IDA升级可能改动主题属性名，届时重跑`gen.py`对照新版`dark`主题重新生成。

## 五、文件

| 文件 | 内容 |
|---|---|
| [onedark-pro-darker/theme.css](onedark-pro-darker/theme.css) | 整套深色主题 |
| [onedark-pro-darker-listing/theme.css](onedark-pro-darker-listing/theme.css) | 只改反汇编视图的版本 |
| [build/gen.py](build/gen.py) | 读取IDA的`dark`主题并映射颜色 |
