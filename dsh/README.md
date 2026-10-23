# DSH推理块与答复块的层级

把DSH聊天界面里展开的推理内容做成一条独立的"过程列"，和答复正文拉开层级。

![默认](images/01-before.png)

![改后](images/02-after.png)

## 一、现状

DSH的答复与推理都没在打包好的样式表里，而是由各插件运行时注入。

| 位置 | 字号 | 行高 | 颜色 | 来源 |
|---|---|---|---|---|
| 答复正文 | 14px | 24px | `--dsw-alias-label-primary`，暗色下 `#f9fafb` | `AssistantMarkdown.module.css` |
| 推理正文 | 13px | 20px | `--dsw-alias-label-tertiary`，暗色下 `#adb2b8` | `dsh-client-ui-primitives` 的compact样式 |

推理还带22px左缩进。差一个字号、一档灰、四像素行高，展开后推理常常比答复还长，两者的起点和重心几乎一样，读到一半要找答复从哪开始。折叠态只有一行摘要，问题不明显；展开态才是要治的地方。

## 二、改法

| 属性 | 默认 | 改后 |
|---|---|---|
| 左侧边界 | 无 | 1px `--dsw-alias-border-l3`，立在推理图标那一列 |
| 正文色 | `#adb2b8` | 与底色混合28%后的 `#82858b` |
| 行高 | 20px | 19px |
| 底部间隔 | 4px | 14px |

细线画在推理图标下方那一列，视觉上把"过程"圈成一栏，比只调颜色更早被识别到；颜色只压一档，仍然可读。答复侧一个值都没动，层级靠对比自动成立。

行内代码与代码块不在覆盖范围内，它们保留自己的配色，避免推理里的代码被一起压灰。

## 三、实测

用真实样式表搭复现页读计算样式，`build/demo.html`加载了DSH前端的`index.css`、主题token、`ReasoningRow.module.css`、`AssistantMarkdown.module.css`，类名与哈希前缀都是原样。

| 探针 | 默认 | 改后 |
|---|---|---|
| 推理正文颜色 | `rgb(173, 178, 184)` | `rgb(130, 133, 139)` |
| 推理正文行高 | 20px | 19px |
| 答复正文颜色 | `rgb(249, 250, 251)` | 不变 |
| 推理栏左边线 | 0px | 1px `rgba(255,255,255,.16)` |
| 推理栏底部间隔 | 4px | 14px |

## 四、安装

界面产物在`app.asar`里，没有用户可写的样式表，不进打包产物的入口只有客户端插件。插件已按DSH的客户端协议写好（`window.__ModuleLoader__.load`注册，`apply()`注入一个`<style>`），在[plugin/](plugin/)下。

安装：

1. 侧边栏打开Plugins页，安装本地目录`plugin/`；或在该profile目录（`~/.dsh/profiles/web`）下执行`pnpm add file:<仓库路径>/dsh/plugin`。
2. 确认该bundle在Plugins页处于启用状态。
3. 重启DSH。

卸载：Plugins页禁用即可，样式随插件一起消失。

这里要说清楚：我没法在这个会话里重启DSH，所以插件没有在真实界面上跑过。已经验证的是插件的注册与注入逻辑（`build/verify-client.mjs`用桩DOM跑通，重复apply不会叠第二份）和样式在真实CSS下的效果。装之前记一下Plugins页的bundle列表，万一加载失败，禁用该项就能回到原样。

不想重启时可以先看效果：在窗口里打开开发者工具，控制台把[dsh-reasoning.css](dsh-reasoning.css)的内容塞进一个`<style>`再挂到`document.head`，刷新即失效。

```js
const s = document.createElement("style");
s.textContent = `<把 dsh-reasoning.css 的内容贴进来>`;
document.head.appendChild(s);
```

开发者工具是否可用取决于打包时有没有开启，打不开就只能走插件。

## 五、边界

- 类名是构建哈希。`_3GBCTG_`对应`@deepseek-ai/dsh-client-ui-chat`当前版本的ReasoningRow，DSH升级后前缀可能变，样式会静默失效。排查办法：`build/extract-css.py`重新抽一次，看前缀。
- 只影响展开态。折叠态只有摘要行，已单独压了一档灰。
- 只管推理。工具调用、命令卡片、子代理的展示没动。

## 六、文件

| 文件 | 内容 |
|---|---|
| [dsh-reasoning.css](dsh-reasoning.css) | 覆盖样式，唯一需要改的源 |
| [plugin/](plugin/) | 客户端插件包，`lib/client.js`由样式生成 |
| [gen.mjs](build/gen.mjs) | 读CSS重新生成插件里的客户端包 |
| [demo.html](build/demo.html) | 复现页，加载真实CSS与真实类名 |
| [shot.mjs](build/shot.mjs) | 无头Edge截图与计算样式对比 |
| [edge.mjs](../build/edge.mjs) | 浏览器路径解析，与deepseek-chat共用 |
| [verify-client.mjs](build/verify-client.mjs) | 桩DOM验证插件注册与注入 |
| [extract-asar.cjs](build/extract-asar.cjs) | 从app.asar取文件 |
| [extract-css.py](build/extract-css.py) | 从插件bundle抽出运行时注入的样式表 |
| [extract-tokens.py](build/extract-tokens.py) | 抽出主题token的CSS |

改了样式后重新生成插件包：

```powershell
node build\gen.mjs
node build\verify-client.mjs
```

`build/index.css`、`build/tokens.css`与`build/css/`是DSH前端样式表的快照，属第三方产物，没有入库。跑复现页与截图前先抽一份，依次执行：

```powershell
node build\extract-asar.cjs "<DSH安装目录>\resources\app.asar" "/dsh/node_modules/@deepseek-ai/dsh-web-frontend/dist/assets/index-BxpfOGf3.css" build\index.css
node build\extract-asar.cjs "<DSH安装目录>\resources\app.asar" "/dsh/node_modules/@deepseek-ai/dsh-client-ui-theme/lib/client.js" build\theme-client.js
python build\extract-tokens.py build\theme-client.js build\tokens.css
python build\extract-css.py build\theme-client.js build\css-theme
```

ReasoningRow与AssistantMarkdown的样式表由`extract-css.py`从`dsh-client-ui-chat/lib/client.js`抽出，放进`build/css/`。

DSH升级后如果类名前缀变了，先用`extract-asar.cjs`把`dsh-client-ui-chat/lib/client.js`取出来，再用`extract-css.py`抽样式，对照新的`ReasoningRow.module.css`改选择器。
