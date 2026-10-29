# Typora主题

一份One Dark Pro Darker的Typora主题，正文与代码都用Cascadia Mono。样式由[build/gen.py](build/gen.py)从根目录的[onedark-pro.json](../onedark-pro.json)生成，色值只有一个来源。

![预览](images/01-preview.png)

## 一、安装

把[onedark-pro-darker.css](onedark-pro-darker.css)放进Typora的用户主题目录：

```text
%APPDATA%\Typora\themes\
```

然后在Typora里打开`偏好设置 - 外观 - 主题`，选择`onedark-pro-darker`。修改后重新选中一次即可刷新，不必重启。

卸载就是删掉那个文件，偏好设置里换回其它主题。

## 二、配色

| 位置 | 取值 | 说明 |
|---|---|---|
| 编辑区底 | `#23272e` | Darker的编辑器背景 |
| 侧栏底 | `#1e2227` | 比正文区暗一档 |
| 正文 | `#abb2bf` | |
| 标题与加粗 | `#dcdcdc` | 比正文亮一档 |
| 引用与次要文字 | `#9da5b4` | |
| 链接 | `#61afef` | |
| 行内代码底 | `#2c313c` | 抬高一层的灰 |
| 围栏代码底 | `#1d1f23` | 比正文区暗，形成内凹 |
| 分隔线与表格线 | `#3e4452` / `#181a1f` | |

代码高亮用VS Code主题里的语法色：关键字紫`#c678dd`、字符串绿`#98c379`、数字与属性橙`#d19a66`、函数蓝`#61afef`、类型黄`#e5c07b`、变量红`#e06c75`、内建cyan`#56b6c2`、注释灰`#7f848e`。

层级主要靠字号、行高和线宽，颜色只用于区分语义：标题只加亮不加色，链接与光标共用一个强调色。

## 三、字体

```css
--font: "Cascadia Mono", "Microsoft YaHei Mono", Consolas, monospace;
```

用Cascadia Mono而不是Cascadia Code，后者带编程连字，`=>`、`!=`会连成图形式样，容易和符号混淆。中文回退到`Microsoft YaHei Mono`，与西文同属等宽，混排时不会跳字体。

正文也想用比例字体的话，把`--font`改成字体栈中比例字体在前、`--monospace`仍指向Cascadia Mono即可，代码块与行内代码不受影响。

## 四、边界

- 只改配色与字体，不动Typora的布局与交互。
- 窗口级元素（侧栏、标题栏、滚动条、搜索框）通过Typora自己的变量定制，覆盖不到的少数控件保持默认外观。
- 导出与打印走独立的亮色样式，避免深底打印耗墨。

## 五、文件

| 文件 | 内容 |
|---|---|
| [onedark-pro-darker.css](onedark-pro-darker.css) | 生成的主题，直接复制到Typora |
| [build/gen.py](build/gen.py) | 读取色板并生成主题 |
| [build/demo.html](build/demo.html) | 预览用的样例页面 |
| [images/01-preview.png](images/01-preview.png) | 预览截图 |
