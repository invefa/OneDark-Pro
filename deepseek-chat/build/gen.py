"""Generate the One Dark Pro Darker skin for chat.deepseek.com.

Reads ../onedark-pro.json (the extracted VSCode palette) and writes:
  onedark-deepseek.user.js   Tampermonkey / Violentmonkey userscript
  onedark-deepseek.css       same stylesheet for Stylus or manual injection

DeepSeek's web app exposes a three layer token system that it defines on
`body[data-ds-dark-theme]`:
  --dsw-static-*    raw palette (neutral-bluish scale, status hues)
  --dsw-alias-*     semantic tokens (bg, label, border, state, markdown)
  --dsw-specific-*  component tokens (sidebar, bubble, menu, selector)
Overriding those tokens recolors the whole UI, including parts that only
appear later during a conversation. The prism `.token.*` classes used by
code blocks are rewritten separately.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PALETTE_PATH = os.path.join(os.path.dirname(ROOT), "onedark-pro.json")

with open(PALETTE_PATH, encoding="utf-8") as fh:
    PALETTE = json.load(fh)

S = PALETTE["surface"]
T = PALETTE["text"]
A = PALETTE["accent"]
ST = PALETTE["status"]
Y = PALETTE["syntax"]
F = PALETTE["flattened"]

EDITOR = S["bg-editor"]
SIDEBAR = S["bg-sidebar"]
INPUT = S["bg-input"]
RAISED = S["bg-raised"]
HOVER = S["bg-hover"]
INACTIVE = S["bg-inactive"]
QUOTE = S["bg-quote"]
LINE_STRONG = S["line-strong"]
LINE_SOFT = S["line-soft"]

FG = T["fg"]
FG_STRONG = T["fg-strong"]
FG_UI = T["fg-ui"]
FG_MUTED = T["fg-muted"]
FG_DIM = T["fg-dim"]
FG_FAINT = T["fg-faint"]

ACCENT = A["accent"]
CURSOR = A["cursor"]
LINK = A["link"]

RED = Y["variable"]
YELLOW = Y["type"]
PURPLE = Y["keyword"]
BLUE = Y["function"]
CYAN = Y["builtin"]
GREEN = Y["string"]
ORANGE = Y["numeric"]
GRAY = Y["comment"]

WHITE = Y["illegal"]

# --- neutral-bluish ramp -----------------------------------------------------
# DeepSeek runs 00 (white) to 1000 (black). The port collapses the 19 steps onto
# the nine neutral values One Dark Pro actually uses, keeping the direction of
# the ramp so any token that reads the scale directly still lands on a sensible
# surface or text colour.
RAMP = {
    "00": WHITE,
    "50": FG,
    "60": FG,
    "75": FG_MUTED,
    "100": FG_MUTED,
    "150": FG_MUTED,
    "200": FG_MUTED,
    "300": FG_MUTED,
    "400": GRAY,
    "500": GRAY,
    "600": FG_DIM,
    "700": FG_FAINT,
    "750": LINE_STRONG,
    "800": INACTIVE,
    "850": RAISED,
    "875": HOVER,
    "900": SIDEBAR,
    "950": EDITOR,
    "1000": LINE_SOFT,
}

# DeepSeek's brand blue scale, folded onto One Dark Pro's three blues.
DEEPSEEK_SCALE = {
    "50": EDITOR,
    "100": RAISED,
    "200": INACTIVE,
    "300": LINE_STRONG,
    "400": LINK,
    "450": CURSOR,
    "500": ACCENT,
    "600": CURSOR,
    "700": ACCENT,
    "700-delete": ACCENT,
    "800": RAISED,
    "900": RAISED,
}

STATIC_EXTRA = {
    "--dsw-static-red-400": RED,
    "--dsw-static-red-500": RED,
    "--dsw-static-red-600": ST["error"],
    "--dsw-static-red-900": "rgba(224, 108, 117, .15)",
    "--dsw-static-green-400": GREEN,
    "--dsw-static-green-500": GREEN,
    "--dsw-static-green-900": "rgba(152, 195, 121, .15)",
    "--dsw-static-amber-400": ORANGE,
    "--dsw-static-amber-500": ORANGE,
    "--dsw-static-amber-600": ORANGE,
    "--dsw-static-amber-900": "rgba(209, 154, 102, .15)",
    "--dsw-static-blue-400": LINK,
    "--dsw-static-blue-450": CURSOR,
    "--dsw-static-blue-500": ACCENT,
    "--dsw-static-blue-600": CURSOR,
    "--dsw-static-blue-800": RAISED,
    "--dsw-static-blue-950": EDITOR,
}

ALIAS = {
    # Surfaces
    "--dsw-alias-bg-base": EDITOR,
    "--dsw-alias-bg-layer-1": RAISED,
    "--dsw-alias-bg-layer-2": INACTIVE,
    "--dsw-alias-bg-layer-3": LINE_STRONG,
    "--dsw-alias-bg-overlay": INACTIVE,
    "--dsw-alias-bg-multi-select": INACTIVE,
    "--dsw-alias-bg-module-platform": INACTIVE,
    "--dsw-alias-bg-skeleton": HOVER,
    # Lines
    "--dsw-alias-border-l1": INACTIVE,
    "--dsw-alias-border-l2": LINE_STRONG,
    "--dsw-alias-border-l2-darkmode-thin": INACTIVE,
    "--dsw-alias-border-l3": FG_FAINT,
    "--dsw-alias-border-l4": "#515a6b",
    "--dsw-alias-border-inverted": RAISED,
    "--dsw-alias-border-inverted2": LINE_STRONG,
    # Interaction
    "--dsw-alias-interactive-bg-hover": HOVER,
    "--dsw-alias-interactive-bg-hover-accent": INACTIVE,
    "--dsw-alias-interactive-bg-active": RAISED,
    "--dsw-alias-interactive-bg-hover-danger": "rgba(224, 108, 117, .15)",
    "--dsw-alias-interactive-bg-hover-solid": HOVER,
    # Brand and buttons
    "--dsw-alias-brand-primary": ACCENT,
    "--dsw-alias-brand-primary-invert": WHITE,
    "--dsw-alias-brand-text": LINK,
    "--dsw-alias-button-primary-fill": ACCENT,
    "--dsw-alias-button-primary-hover": CURSOR,
    "--dsw-alias-button-primary-dimmed": INACTIVE,
    "--dsw-alias-button-info-fill": ACCENT,
    "--dsw-alias-button-info-hover": CURSOR,
    "--dsw-alias-button-elevated-fill": INACTIVE,
    "--dsw-alias-button-floating-fill": INACTIVE,
    "--dsw-alias-button-floating-hover": LINE_STRONG,
    "--dsw-alias-button-ghost-active-fill": RAISED,
    "--dsw-alias-button-ghost-active-hover": INACTIVE,
    "--dsw-alias-button-ghost-active-border": ACCENT,
    "--dsw-alias-button-tool-bar-fill": "rgba(44, 49, 58, .6)",
    "--dsw-alias-button-tool-bar-hover": "rgba(44, 49, 58, .8)",
    "--dsw-alias-button-tool-bar-fill-invisible": "rgba(24, 26, 31, .36)",
    "--dsw-alias-button-contrast-fill": FG,
    # Text
    # One Dark Pro keeps almost every UI text on #abb2bf and drops to #9da5b4
    # only for status-like copy, so the site's four text levels collapse onto
    # three: primary, secondary and tertiary all read as body text, while
    # caption and dimmed carry the muted roles.
    "--dsw-alias-label-primary": FG,
    "--dsw-alias-label-primary-dimmed": FG_MUTED,
    "--dsw-alias-label-secondary": FG,
    "--dsw-alias-label-tertiary": FG,
    "--dsw-alias-label-caption": FG_MUTED,
    "--dsw-alias-label-dimmed": FG_FAINT,
    "--dsw-alias-label-primary-foreground": WHITE,
    "--dsw-alias-label-primary-inverted": EDITOR,
    # Markdown
    "--dsw-alias-markdown-code-block": SIDEBAR,
    "--dsw-alias-markdown-code-block-banner": EDITOR,
    "--dsw-alias-markdown-inline-code": RAISED,
    "--dsw-alias-markdown-citation": RAISED,
    "--dsw-alias-markdown-tag": RAISED,
    "--dsw-alias-markdown-placeholder": RAISED,
    "--dsw-alias-markdown-code-segment-selected": INACTIVE,
    "--dsw-alias-markdown-code-segment-unselected": RAISED,
    # Scrollbars and overlays
    "--dsw-alias-scrollbar-bg-l1": LINE_STRONG,
    "--dsw-alias-scrollbar-bg-l2": FG_FAINT,
    "--dsw-alias-scrollbar-hover-l1": FG_FAINT,
    "--dsw-alias-scrollbar-hover-l2": "#515a6b",
    "--dsw-alias-toast-bg": INACTIVE,
    "--dsw-alias-tooltip-bg": INACTIVE,
    # Component tokens
    "--dsw-specific-bubble": HOVER,
    "--dsw-specific-bubble-highlight": INACTIVE,
    "--dsw-specific-input-major": INPUT,
    "--dsw-specific-login-input": SIDEBAR,
    "--dsw-specific-menu": INACTIVE,
    "--dsw-specific-selector": RAISED,
    "--dsw-specific-sidebar-fill": SIDEBAR,
    "--dsw-specific-sidebar-nav-item-hover": HOVER,
    "--dsw-specific-sidebar-nav-item-active": INACTIVE,
    "--dsw-specific-sidebar-nav-item-active-accent": LINE_STRONG,
    # Misc
    "--dsw-linear-gradient-think": "linear-gradient(180deg, {} 20.19%, rgba(35, 39, 46, 0) 100%)".format(EDITOR),
    "--scroll-color": "rgba(78, 86, 102, .6)",
    "--dsl-a-text-color": LINK,
    "--dsl-a-text-hover-color": CURSOR,
}

# --- prism ------------------------------------------------------------------
# Each entry is a full descendant selector suffix, joined onto CODE with a space.
# DeepSeek ships a one-dark style prism theme already; these values swap it for
# One Dark Pro's own assignment.
PRISM = {
    GRAY: [
        ".token.comment", ".token.prolog", ".token.doctype", ".token.cdata",
        ".language-markdown .token.hr.punctuation",
        ".language-markdown .token.blockquote.punctuation",
    ],
    FG: [
        ".token.punctuation", ".token.parameter",
        ".language-markdown .token.table-header",
        ".language-json .token.operator",
    ],
    RED: [
        ".token.tag", ".token.tag .token.punctuation", ".token.deleted", ".token.important",
        ".token.delimiter.important", ".token.selector", ".token.selector .parent",
        ".token.property", ".token.property-access", ".token.variable", ".token.key", ".token.regex",
        ".token.keyword-this", ".token.this",
        ".language-scss .token.variable",
        ".language-markdown .token.list.punctuation",
    ],
    YELLOW: [".token.class-name"],
    PURPLE: [
        ".token.keyword", ".token.operator", ".token.atrule .token.rule", ".token.combinator",
        ".token.pseudo-class", ".token.pseudo-element",
    ],
    BLUE: [
        ".token.function", ".token.selector .token.class", ".token.selector .token.id",
        ".language-markdown .token.title",
        ".language-markdown .token.title .token.punctuation",
        ".language-markdown .token.url .token.content",
        ".language-markdown .token.url-link",
    ],
    CYAN: [".token.builtin", ".token.keyword-array", ".token.package"],
    GREEN: [
        ".token.string", ".token.attr-value", ".token.inserted", ".token.color",
        ".token.selector .value", ".token.string .token.url-link",
        ".language-markdown .token.code",
    ],
    ORANGE: [".token.attr-name", ".token.boolean", ".token.boolean.important", ".token.number",
             ".token.constant", ".token.selector .attribute", ".token.unit"],
}

RAINBOW = [
    ("brace-level-1", ORANGE), ("brace-level-2", PURPLE), ("brace-level-3", CYAN),
    ("brace-level-4", YELLOW), ("brace-level-5", ORANGE), ("brace-level-6", PURPLE),
    ("brace-level-7", CYAN), ("brace-level-8", YELLOW), ("brace-level-9", ORANGE),
    ("brace-level-10", PURPLE), ("brace-level-11", CYAN), ("brace-level-12", YELLOW),
]

SCOPE = "body[data-ds-dark-theme]"
CODE = SCOPE + " .md-code-block.md-code-block-dark"


def token_block(extra_alias=None):
    """Emit the design-token override block shared by every DSH/DeepSeek skin."""
    lines = [SCOPE + " {"]
    lines.append("  /* raw palette: neutral ramp */")
    for step, value in RAMP.items():
        lines.append("  --dsw-static-neutral-bluish-{}: {} !important;".format(step, value))
    lines.append("")
    lines.append("  /* raw palette: brand blues */")
    for step, value in DEEPSEEK_SCALE.items():
        lines.append("  --dsw-static-deepseek-{}: {} !important;".format(step, value))
    lines.append("")
    lines.append("  /* raw palette: status hues */")
    for name, value in STATIC_EXTRA.items():
        lines.append("  {}: {} !important;".format(name, value))
    lines.append("")
    lines.append("  /* semantic layer */")
    for name, value in ALIAS.items():
        lines.append("  {}: {} !important;".format(name, value))
    for name, value in (extra_alias or {}).items():
        lines.append("  {}: {} !important;".format(name, value))
    lines.append("}")
    lines.append("")
    return lines


def build_css():
    out = []
    out.append("/* One Dark Pro Darker for chat.deepseek.com")
    out.append("   Palette extracted from VSCode theme zhuangtongfa.material-theme {}.".format(PALETTE["meta"]["version"]))
    out.append("   Applied to DeepSeek's own design tokens, so newly rendered parts follow too. */")
    out.append("")

    out.extend(token_block())

    out.append("/* thinking block: a process column under the answer")
    out.append("   The site already ships the icon, the left rule and the 22px indent, but it colours")
    out.append("   reasoning with label-secondary, which in this mapping is the body colour, so the block")
    out.append("   needs its own step down. */")
    out.append("{} .ds-think-content .ds-markdown {{\n  color: {};\n  line-height: 22px;\n}}".format(SCOPE, GRAY))
    out.append("")
    out.append("/* everything inside reasoning is capped at the body grey, so bold and\n   headings carry weight instead of brightness; code and links are excluded */")
    out.append("{} .ds-think-content :not(pre):not(code):not(.token):not(a) {{\n  color: {} !important;\n}}".format(SCOPE, GRAY))
    out.append("")
    out.append("{} .ds-think-content .ds-markdown :is(p, .ds-markdown-paragraph) {{\n  margin: 8px 0;\n}}".format(SCOPE))
    out.append("")

    out.append("/* code block syntax */")
    for color, suffixes in PRISM.items():
        selectors = ",\n".join("{} {}".format(CODE, suffix) for suffix in suffixes)
        out.append(selectors + " {{\n  color: {};\n}}".format(color))
        out.append("")

    out.append("/* code block base text and background */")
    out.append("{0} code[class*=language-],\n{0} pre[class*=language-] {{\n  color: {1};\n  background: none;\n}}".format(CODE, FG))
    out.append("")
    out.append("{}.md-code-block {{\n  background: {};\n  border-color: {};\n}}".format(SCOPE, SIDEBAR, LINE_STRONG))
    out.append("")

    out.append("/* rainbow brackets and line numbers */")
    for level, color in RAINBOW:
        out.append("{} .rainbow-braces .token.token.punctuation.{} {{\n  color: {};\n}}".format(CODE, level, color))
    out.append("")
    out.append("{0} .line-numbers-rows > span:before {{\n  color: {1};\n}}".format(CODE, FG_FAINT))
    out.append("{0} .line-highlight,\n{0} .line-highlight:before {{\n  background: {1};\n}}".format(CODE, RAISED))
    out.append("")

    out.append("/* selection */")
    out.append("{} ::selection {{\n  background: {};\n}}".format(SCOPE, F["editor-selectionbackground"]))
    out.append("")
    return "\n".join(out)


def build_userscript(css):
    header = """// ==UserScript==
// @name         One Dark Pro Darker for DeepSeek Chat
// @namespace    local.onedarkpro.deepseek
// @version      1.4.0
// @description  Apply the One Dark Pro Darker palette to chat.deepseek.com by remapping its design tokens.
// @match        https://chat.deepseek.com/*
// @updateURL    https://github.com/invefa/OneDark-Pro/raw/refs/heads/main/deepseek-chat/onedark-deepseek.user.js
// @downloadURL  https://github.com/invefa/OneDark-Pro/raw/refs/heads/main/deepseek-chat/onedark-deepseek.user.js
// @run-at       document-start
// @grant        none
// ==/UserScript==
"""
    body = """
(function () {
    "use strict";

    var CONFIG = {
        // set to false to switch the whole skin off
        enabled: true,
        // these tokens only exist in dark mode; switch the site to dark first
        requireDarkAttribute: true
    };

    if (!CONFIG.enabled) return;

    var CSS = String.raw`__CSS__`;

    function inject() {
        if (document.getElementById("onedark-pro-darker")) return;
        if (CONFIG.requireDarkAttribute && !document.body.hasAttribute("data-ds-dark-theme")) {
            // in light mode leave the page alone and wait for the dark theme attribute
            var wait = new MutationObserver(function () {
                if (document.body.hasAttribute("data-ds-dark-theme")) {
                    wait.disconnect();
                    inject();
                }
            });
            wait.observe(document.body, { attributes: true, attributeFilter: ["data-ds-dark-theme"] });
            return;
        }
        var style = document.createElement("style");
        style.id = "onedark-pro-darker";
        style.textContent = CSS;
        document.head.appendChild(style);
        console.log("[One Dark Pro Darker] skin injected");
    }

    function start() {
        if (document.body) {
            inject();
        } else {
            document.addEventListener("DOMContentLoaded", inject, { once: true });
        }
    }

    start();
})();
"""
    return header + body.replace("__CSS__", css.replace("`", "\\`").replace("${", "\\${"))


def main():
    css = build_css()
    with open(os.path.join(ROOT, "onedark-deepseek.css"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(css)
        fh.write("\n")
    with open(os.path.join(ROOT, "onedark-deepseek.user.js"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build_userscript(css))
    print("palette:", PALETTE_PATH)
    print("css lines:", css.count("\n"))
    print("wrote", ROOT)


if __name__ == "__main__":
    main()
