# Windows Terminal配色

One Dark Pro Darker的终端配色。装的是Windows Terminal的方案（scheme），16个ANSI色加背景、前景、光标、选中底色。

## 一、安装

方案文件有两份：终端色那份是默认，语法色那份作为对照。两种装法：

脚本合并（推荐，两个方案一起写入并自动备份）：

```powershell
python windows-terminal\apply.py
```

手工：把json里的对象贴进`settings.json`的`schemes`数组，再把`profiles.defaults.colorScheme`改成`"One Dark Pro Darker"`。

默认路径：

```text
%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json
```

保存后Windows Terminal会自己重载，不用重启。

## 二、参数

| 键 | 值 | 说明 |
|---|---|---|
| `background` | `#23272E` | 编辑器底 |
| `foreground` | `#ABB2BF` | 正文 |
| `cursorColor` | `#ABB2BF` | 与正文字同色 |
| `selectionBackground` | `#3E4452` | 分隔线灰，不用亮色块 |
| `black` / `white` | `#3F4451` / `#D7DAE0` | |
| `red` / `green` / `yellow` / `blue` | `#E05561` / `#8CC265` / `#D18F52` / `#4AA5F0` | 主题的终端色 |
| `purple` / `cyan` | `#C162DE` / `#42B3C2` | |
| `bright*` | 同系提亮 | `brightBlack` 为 `#4F5666` |

终端色与语法色在One Dark Pro里是两套。终端那套（`#8CC265`、`#42B3C2`）比编辑器的语法色（`#98C379`、`#56B6C2`）暗一档，这是作者为整屏命令行输出做的调整；换成语法色后满屏输出会偏粉彩、发白，所以这里用终端色。

### 语法色变体

仓库里另有一份`One Dark Pro Darker Syntax`，十六个槽位取自编辑器语法色，用来和终端色那套对比。

| 槽位 | 终端色方案 | 语法色方案 |
|---|---|---|
| red | `#E05561` | `#E06C75` |
| green | `#8CC265` | `#98C379` |
| yellow | `#D18F52` | `#D19A66` |
| blue | `#4AA5F0` | `#61AFEF` |
| purple | `#C162DE` | `#C678DD` |
| cyan | `#42B3C2` | `#56B6C2` |
| white | `#D7DAE0` | `#ABB2BF` |
| brightBlack | `#4F5666` | `#7F848E` |

切换方式：`设置 - 配色方案`里选另一个，或者把`profiles.defaults.colorScheme`改成`"One Dark Pro Darker Syntax"`。`apply.py`只负责把两个方案写进去，不改变当前选中的是哪个。

终端色与语法色不应混用：语法色是按稀疏高亮调的，整屏输出会发白；终端色按满屏文字调的，单独看比编辑器暗一档。要两者完全一致只能让程序输出真彩色，绕过终端方案。

## 三、边界

- 只改配色。字体、字号、透明度、光标形状仍由`profiles.defaults`决定。
- `useAcrylic`与`opacity`会让背景色透出桌面，实测颜色会偏亮；要完全按色值显示就把`useAcrylic`关掉、`opacity`设100。
- 方案只对Windows Terminal生效。cmd.exe直接跑、或其他终端不走这套。
- 颜色由色板生成，不手改生成物。改映射落在`build/gen.py`，重新生成后再跑`apply.py`。

## 四、文件

| 文件 | 内容 |
|---|---|
| [onedark-pro-darker.json](onedark-pro-darker.json) | 终端色方案 |
| [onedark-pro-darker-syntax.json](onedark-pro-darker-syntax.json) | 语法色方案 |
| [apply.py](apply.py) | 合并脚本，改前备份，重复执行不重复写 |
| [build/gen.py](build/gen.py) | 读取色板生成方案 |
