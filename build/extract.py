"""Extract the effective One Dark Pro Darker palette from the installed VSCode theme.

Reads the theme JSON that the extension actually renders, writes a CSS variable
sheet, a JSON token map and a palette preview, and prints Markdown tables.
"""

import glob
import json
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXT_ROOT = os.path.expandvars(r"%USERPROFILE%\.vscode\extensions")
THEME_GLOB = os.path.join(EXT_ROOT, "zhuangtongfa.material-theme-*", "themes", "OneDark-Pro-darker.json")
THEME_PATH = sorted(glob.glob(THEME_GLOB))[-1]
PKG_PATH = os.path.join(os.path.dirname(os.path.dirname(THEME_PATH)), "package.json")

with open(PKG_PATH, encoding="utf-8") as fh:
    VERSION = json.load(fh)["version"]
with open(THEME_PATH, encoding="utf-8") as fh:
    THEME = json.load(fh)

COLORS = {k.lower(): v.lower() for k, v in THEME["colors"].items()}


def c(key):
    key = key.lower()
    if key not in COLORS:
        raise KeyError(key)
    return COLORS[key]


def composite(raw, base):
    """Flatten an 8-digit hex colour onto an opaque background."""
    alpha = int(raw[7:9], 16) / 255
    back = [int(base[i:i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(int(raw[i:i + 2], 16) * alpha + back[j] * (1 - alpha))
             for j, i in enumerate((1, 3, 5))]
    return "#" + "".join(f"{v:02x}" for v in mixed)


SURFACE = [
    ("bg-editor", "editor.background"),
    ("bg-sidebar", "sideBar.background"),
    ("bg-input", "input.background"),
    ("bg-raised", "editor.lineHighlightBackground"),
    ("bg-hover", "list.hoverBackground"),
    ("bg-inactive", "list.inactiveSelectionBackground"),
    ("bg-quote", "textBlockQuote.background"),
    ("line-strong", "panel.border"),
    ("line-soft", "editorGroup.border"),
]

TEXT = [
    ("fg", "editor.foreground"),
    ("fg-strong", "tab.activeForeground"),
    ("fg-ui", "activityBar.foreground"),
    ("fg-muted", "statusBar.foreground"),
    ("fg-dim", "titleBar.inactiveForeground"),
    ("fg-faint", "editorLineNumber.foreground"),
]

ACCENT = [
    ("accent", "activityBarBadge.background"),
    ("cursor", "editorCursor.foreground"),
    ("link", "textLink.foreground"),
]

STATUS = [
    ("error", "editorError.foreground"),
    ("warning", "editorWarning.foreground"),
    ("added", "editorGutter.addedBackground"),
    ("modified", "editorGutter.modifiedBackground"),
    ("deleted", "editorGutter.deletedBackground"),
]

# name, 用途, scope
SYNTAX = [
    ("text", "默认文本与标点", "variable.parameter.function"),
    ("variable", "变量名", "variable"),
    ("keyword", "关键字", "keyword"),
    ("keyword-op", "关键字运算符", "keyword.operator.word"),
    ("operator", "运算符", "keyword.operator"),
    ("function", "函数调用", "entity.name.function"),
    ("type", "类与类型", "entity.name.type"),
    ("namespace", "命名空间", "entity.name.namespace"),
    ("builtin", "内置函数", "support.function"),
    ("numeric", "数字与常量", "constant.numeric"),
    ("string", "字符串", "string"),
    ("comment", "注释", "comment"),
    ("tag", "标签", "entity.name.tag"),
    ("attribute", "属性名", "entity.other.attribute-name"),
    ("illegal", "非法内容", "invalid.illegal"),
    ("error-token", "错误标记", "token.error-token"),
    ("md-heading", "Markdown 标题", "markup.heading"),
    ("md-section", "Markdown 章节", "entity.name.section"),
    ("md-bold", "Markdown 加粗", "markup.bold"),
    ("md-quote", "Markdown 引用", "markup.quote.markdown"),
    ("diff-inserted", "差异插入行", "markup.inserted"),
    ("diff-deleted", "差异删除行", "markup.deleted"),
    ("diff-changed", "差异变更行", "markup.changed.diff"),
]

TERMINAL = [(n.lower(), "terminal.ansi" + n) for n in
            ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White")]
TERMINAL_BRIGHT = [("bright-" + n.lower(), "terminal.ansiBright" + n) for n in
                   ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White")]

TRANSLUCENT = [
    ("editor.selectionBackground", "editor.background"),
    ("editor.selectionHighlightBackground", "editor.background"),
    ("editor.wordHighlightBackground", "editor.background"),
    ("editor.findMatchBackground", "editor.background"),
    ("editor.findMatchHighlightBackground", "editor.background"),
    ("editorIndentGuide.activeBackground1", "editor.background"),
    ("editorWhitespace.foreground", "editor.background"),
    ("editorRuler.foreground", "editor.background"),
    ("terminal.selectionBackground", "editor.background"),
    ("scrollbarSlider.background", "sideBar.background"),
    ("scrollbarSlider.hoverBackground", "sideBar.background"),
    ("scrollbarSlider.activeBackground", "sideBar.background"),
]


def scope_color(scope):
    hits = []
    for rule in THEME["tokenColors"]:
        scopes = rule["scope"]
        if isinstance(scopes, str):
            scopes = [s.strip() for s in scopes.split(",")]
        if scope in scopes and rule["settings"].get("foreground"):
            hits.append(rule["settings"]["foreground"].lower())
    return sorted(set(hits))


def pairs(items):
    return [(name, c(key)) for name, key in items]


def syntax_pairs():
    out = []
    for name, _role, scope in SYNTAX:
        colors = scope_color(scope)
        if not colors:
            raise KeyError("scope without colour: " + scope)
        out.append((name, colors[0]))
    return out


def write_css():
    lines = [
        "/* One Dark Pro Darker, extracted from zhuangtongfa.material-theme {}".format(VERSION),
        "   Source: themes/OneDark-Pro-darker.json",
        "   Translucent editor overlays are flattened onto editor.background. */",
        "",
        ":root {",
    ]

    def block(title, items, prefix=""):
        lines.append("  /* " + title + " */")
        for name, value in items:
            lines.append("  --odp-{}{}: {};".format(prefix, name, value))
        lines.append("")

    block("surface", pairs(SURFACE))
    block("text", pairs(TEXT))
    block("accent", pairs(ACCENT))
    block("status", pairs(STATUS))
    block("syntax", syntax_pairs())
    block("terminal", pairs(TERMINAL + TERMINAL_BRIGHT), "ansi-")

    lines.append("  /* translucent overlays, flattened */")
    for key, base in TRANSLUCENT:
        flat = composite(c(key), c(base))
        lines.append("  --odp-flat-{}: {};".format(key.replace(".", "-").lower(), flat))
    lines.append("}")
    lines.append("")

    with open(os.path.join(OUT, "onedark-pro.css"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def write_json():
    doc = {
        "meta": {
            "theme": THEME["name"],
            "variant": "One Dark Pro Darker",
            "extension": "zhuangtongfa.material-theme",
            "version": VERSION,
            "type": THEME["type"],
            "source": "themes/OneDark-Pro-darker.json",
        },
        "surface": dict(pairs(SURFACE)),
        "text": dict(pairs(TEXT)),
        "accent": dict(pairs(ACCENT)),
        "status": dict(pairs(STATUS)),
        "syntax": dict(syntax_pairs()),
        "syntaxScopes": {name: scope for name, _role, scope in SYNTAX},
        "terminal": dict(pairs(TERMINAL)),
        "terminalBright": dict(pairs(TERMINAL_BRIGHT)),
        "flattened": {key.replace(".", "-").lower(): composite(c(key), c(base)) for key, base in TRANSLUCENT},
        "workbenchColors": COLORS,
    }
    with open(os.path.join(OUT, "onedark-pro.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


FONT_DIR = r"C:\Windows\Fonts"


def load(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def write_png():
    width, margin = 600, 20
    content = width - margin * 2

    title_font = load("segoeuib.ttf", 16)
    sub_font = load("segoeui.ttf", 10)
    label_font = load("segoeuib.ttf", 9)
    role_font = load("segoeui.ttf", 8)
    hex_font = load("consola.ttf", 9)

    img = Image.new("RGB", (width, 1200), c("editor.background"))
    draw = ImageDraw.Draw(img)
    state = {"y": margin}

    def section(title, items, per_row, chip_h, role_labels):
        y = state["y"]
        draw.text((margin, y), title.upper(), font=label_font, fill=c("statusBar.foreground"))
        y += 15
        gap = 8
        chip_w = (content - gap * (per_row - 1)) / per_row
        label_h = 12 if role_labels else 0
        step = chip_h + label_h + 16
        for index, (name, value) in enumerate(items):
            col, row = index % per_row, index // per_row
            x = margin + col * (chip_w + gap)
            top = y + row * step
            if role_labels:
                draw.text((x, top), name, font=role_font, fill=c("statusBar.foreground"))
            cy = top + label_h
            draw.rounded_rectangle([x, cy, x + chip_w, cy + chip_h], radius=3,
                                   fill=value, outline=c("editorGroup.border"))
            tw = draw.textlength(value, font=hex_font)
            draw.text((x + (chip_w - tw) / 2, cy + chip_h + 3), value, font=hex_font,
                      fill=scope_color("comment")[0])
        rows = (len(items) + per_row - 1) // per_row
        state["y"] = y + rows * step + 6

    y0 = margin
    draw.text((margin, y0), "One Dark Pro Darker", font=title_font, fill=c("tab.activeForeground"))
    draw.text((margin, y0 + 22), "zhuangtongfa.material-theme {}".format(VERSION), font=sub_font,
              fill=c("titleBar.inactiveForeground"))
    state["y"] = y0 + 46

    section("surface", pairs(SURFACE), 9, 34, False)
    section("text", pairs(TEXT), 6, 30, False)
    section("accent and status", pairs(ACCENT) + pairs(STATUS), 8, 26, False)
    section("syntax", syntax_pairs(), 8, 30, True)
    section("terminal", pairs(TERMINAL), 8, 28, False)
    section("terminal bright", pairs(TERMINAL_BRIGHT), 8, 28, False)

    img.crop((0, 0, width, int(state["y"]) + 10)).save(os.path.join(OUT, "palette.png"))


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(out)


def print_tables():
    print("\n[surface]")
    print(md_table(["name", "hex"], pairs(SURFACE)))
    print("\n[text]")
    print(md_table(["name", "hex"], pairs(TEXT)))
    print("\n[accent]")
    print(md_table(["name", "hex"], pairs(ACCENT)))
    print("\n[status]")
    print(md_table(["name", "hex"], pairs(STATUS)))
    print("\n[syntax]")
    print(md_table(["name", "scope", "hex"], [[n, s, scope_color(s)[0]] for n, _r, s in SYNTAX]))
    print("\n[terminal]")
    print(md_table(["name", "normal", "bright"],
                   [[n, c(k), c(kb)] for (n, k), (_n2, kb) in zip(TERMINAL, TERMINAL_BRIGHT)]))
    print("\n[flattened]")
    print(md_table(["key", "raw", "flat"], [[k, c(k), composite(c(k), c(b))] for k, b in TRANSLUCENT]))
    print("\ncounts: colors={} tokenRules={}".format(len(COLORS), len(THEME["tokenColors"])))


if __name__ == "__main__":
    write_css()
    write_json()
    write_png()
    print_tables()
    print("\nwrote:", OUT)
