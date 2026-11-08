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
| `cursorColor` | `#ABB2BF` | 与正文字同色 |
| `selectionBackground` | `#3E4452` | 分隔线灰 |
| `black` / `white` | `#3F4451` / `#D7DAE0` | 中性色，取自主题终端色 |
| `red` | `#E06C75` | 语法变量色 |
| `green` | `#98C379` | 语法字符串色 |
| `yellow` | `#E5C07B` | 语法类型色 |
| `blue` | `#61AFEF` | 语法函数色 |
| `purple` | `#C678DD` | 语法关键字色 |
| `cyan` | `#56B6C2` | 语法内建色 |
| `brightBlack` | `#7F848E` | 注释灰，对应SGR 90 |
| `bright*` 其余 | 同色相提亮15% | |

ANSI 槽位用语法色，不用主题里的终端色（`#8CC265`、`#42B3C2` 那一组）。主题作者给终端另配了一套偏暗的颜色，命令行工具按色号取色时会比编辑器里的同语义颜色暗一档。

`brightBlack` 对应 SGR `90`，clerk 用它画行号与辅助说明。这里填注释灰 `#7F848E`，与编辑器注释一致。

## 三、边界

- 只改配色。字体、字号、透明度、光标形状仍由`profiles.defaults`决定。
- `useAcrylic`与`opacity`会让背景色透出桌面，实测颜色会偏亮；要完全按色值显示就把`useAcrylic`关掉、`opacity`设100。
- 方案只对Windows Terminal生效。cmd.exe直接跑、或其他终端不走这套。
- 颜色由色板生成，不手改生成物。改映射落在`build/gen.py`，重新生成后再跑`apply.py`。

## 四、文件

| 文件 | 内容 |
|---|---|
| [onedark-pro-darker.json](onedark-pro-darker.json) | 方案对象，可直接贴进settings.json |
| [apply.py](apply.py) | 合并脚本，改前备份，重复执行不重复写 |
| [build/gen.py](build/gen.py) | 读取色板生成方案 |
