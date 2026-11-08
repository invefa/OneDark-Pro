# Windows Terminal配色

One Dark Pro Darker的终端配色。装的是Windows Terminal的方案（scheme），16个ANSI色加背景、前景、光标、选中底色。

## 一、安装

方案文件是[onedark-pro-darker.json](onedark-pro-darker.json)。两种装法：

脚本合并（推荐，自动备份）：

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
| `cursorColor` | `#528BFF` | 光标，与VS Code一致 |
| `selectionBackground` | `#3E4452` | 选中底色用分隔线灰，不用亮色块 |
| `black` / `white` | `#3F4451` / `#D7DAE0` | |
| `red`/`green`/`yellow`/`blue` | `#E05561`/`#8CC265`/`#D18F52`/`#4AA5F0` | 取自主题的终端色，不是编辑器语法色 |
| `purple`/`cyan` | `#C162DE`/`#42B3C2` | |
| `bright*` | 同系提亮 | |

终端色与语法色是两套。One Dark Pro原主题里终端用`#8CC265`、`#42B3C2`这类更暗的色，编辑器语法才用`#98C379`、`#56B6C2`；这里跟着终端那套。

之前`schemes`里那份`One Dark Pro`的蓝位写成了`#56B6C2`（那是cyan的值），新方案按主题JSON取值。

## 三、边界

- 只改配色。字体、字号、透明度、光标形状仍由`profiles.defaults`决定。
- `useAcrylic`与`opacity`会让背景色透出桌面，实测颜色会偏亮；要完全按色值显示就把`useAcrylic`关掉、`opacity`设100。
- 方案只对Windows Terminal生效。cmd.exe直接跑、或其他终端不走这套。

## 四、文件

| 文件 | 内容 |
|---|---|
| [onedark-pro-darker.json](onedark-pro-darker.json) | 方案对象，可直接贴进settings.json |
| [apply.py](apply.py) | 合并脚本，改前备份，重复执行不重复写 |
