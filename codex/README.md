# Codex配色

把One Dark Pro Darker套到Codex桌面版。改的是`~/.codex/config.toml`里的外观段。

Codex的外观分两层，能改的只有一层：

| 层 | 配置 | 可否自定义 |
|---|---|---|
| 界面色 | `[desktop.appearanceDarkChromeTheme]` | 可以，键值自由填 |
| 代码块 | `appearanceDarkCodeThemeId` | 只能选内置主题id，不能填色值 |

## 一、参数

| 键 | 值 | 依据 |
|---|---|---|
| `surface` | `#23272e` | 编辑器底 |
| `ink` | `#abb2bf` | 正文 |
| `accent` | `#4d78cc` | 强调 |
| `contrast` | `60` | 应用原有取值，未动 |
| `opaqueWindows` | `false` | 保留原值 |
| `diffAdded` | `#98c379` | 差异新增 |
| `diffRemoved` | `#e06c75` | 差异删除 |
| `skill` | `#c162de` | 应用原有的紫，保留 |
| `fonts.code` | `Cascadia Code`, `Microsoft YaHei Mono`, `Consolas` | 与VSCode编辑器字体栈一致 |

`surface`原来是One Dark基础版的`#282c34`，换成Darker的`#23272e`。

## 二、应用

脚本只改上表这几个键，其余内容原样保留，写入前自动备份：

```powershell
python codex\apply.py
```

默认改`~/.codex/config.toml`，也可以传路径。重复执行不会重复写。

手工应用就把[theme.toml](theme.toml)里的段落并进`config.toml`，同名键覆盖。

重启Codex生效。恢复用同目录下的`config.toml.bak-<时间戳>`覆盖回去。

## 三、边界

- 代码块主题是应用内置的，只有id可选，没有自定义入口。`appearanceDarkCodeThemeId`当前是`one`，具体对应哪套主题由应用自己校验，填错会被忽略。要换在设置的APPEARANCE页里选。
- 只配了深色外观。`[desktop.appearanceLightChromeTheme]`与`appearanceLightCodeThemeId`没动。
- 其余应用内部的硬编码色不在这些键的管辖范围内，改不动。
- 中英混排能否列对齐取决于字体本身。`Microsoft YaHei Mono`的汉字宽度是数字的1.82倍，不是严格的2倍；VSCode里能对齐是因为Monaco编辑器按两列处理CJK，普通网页文本没有这一步。

## 四、文件

| 文件 | 内容 |
|---|---|
| [theme.toml](theme.toml) | 要合并的配置段 |
| [apply.py](apply.py) | 合并脚本，带备份 |
