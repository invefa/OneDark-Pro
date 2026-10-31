# OpenCode主题

One Dark Pro Darker的OpenCode主题。OpenCode内置了`one-dark`，那是Atom One Dark基础版，底色`#282c34`；这份用的是Darker变体，底色`#23272e`。

主题由[build/gen.py](build/gen.py)从根目录的[onedark-pro.json](../onedark-pro.json)生成，色值只有一个来源。

## 一、安装

主题文件放进用户主题目录，并在`opencode.json`里选中：

```text
~/.config/opencode/themes/onedark-pro-darker.json
~/.config/opencode/opencode.json   ->  "theme": "onedark-pro-darker"
```

也可以只在某个项目里生效：把json放到项目下的`.opencode/themes/`，同样在配置里写`theme`。

OpenCode要求终端支持truecolor。检查`echo $COLORTERM`，输出`truecolor`或`24bit`即可；不是的话在shell配置里加`COLORTERM=truecolor`。

## 二、映射

OpenCode的主题是JSON，50个键，每个键给`dark`与`light`两个值。色值可以写十六进制，也可以先在`defs`里命名再引用，这里用后者。

| OpenCode键 | 取值 | 来源 |
|---|---|---|
| `background` | `#23272e` | 编辑器底色 |
| `backgroundPanel` | `#1e2227` | 侧栏 |
| `backgroundElement` | `#2c313c` | 浮起层 |
| `text` | `#abb2bf` | 正文 |
| `textMuted` | `#7f848e` | 注释灰 |
| `border` / `borderActive` / `borderSubtle` | `#3e4452` / `#495162` / `#323842` | 两级线 |
| `primary` / `info` | `#61afef` / `#56b6c2` | 链接与提示 |
| `accent` | `#c678dd` | 关键字紫 |
| `error` / `warning` / `success` | `#e06c75` / `#e5c07b` / `#98c379` | 状态色 |
| `syntaxKeyword`…`syntaxPunctuation` | 同VS Code语法色 | |
| `markdownHeading` / `markdownStrong` | `#dcdcdc` | 比正文亮一档 |
| `diffAddedBg` / `diffRemovedBg` | `#1f2a24` / `#2c2327` | 差异行底 |

## 三、边界

- `dark`与`light`给的是同一组值。色板只有深色一套，OpenCode要求两个槽都填，浅色模式下仍是深色。
- 只改颜色。OpenCode的布局、边框宽度、圆角由自身决定，主题JSON没有对应键。
- 主题只作用于OpenCode自己的界面。终端本身的背景、光标形状仍由终端配置决定。

## 四、文件

| 文件 | 内容 |
|---|---|
| [onedark-pro-darker.json](onedark-pro-darker.json) | 生成的主题，复制到用户主题目录 |
| [build/gen.py](build/gen.py) | 读取色板并生成主题 |
