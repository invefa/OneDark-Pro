"""Generate the One Dark Pro Darker skin for the DSH web interface.

The palette mapping lives in the DeepSeek web skin because both surfaces use the
same `--dsw-*` design tokens; this generator loads that module and reuses its
`token_block()`, then adds the tokens DSH declares on top plus the reasoning rules.
"""

import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_GEN = os.path.join(os.path.dirname(ROOT), "deepseek-chat", "build", "gen.py")

spec = importlib.util.spec_from_file_location("site_skin", SITE_GEN)
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)

ACCENT = site.ACCENT
FG = site.FG
FG_MUTED = site.FG_MUTED
FG_STRONG = site.FG_STRONG
GREEN = site.GREEN
RED = site.RED
RAISED = site.RAISED
INACTIVE = site.INACTIVE
LINK = site.LINK
SCOPE = site.SCOPE
CODE_FONT = '"Cascadia Mono", Consolas, "Microsoft YaHei Mono", monospace'
FLAT_SELECTION = site.F["editor-selectionbackground"]

# Tokens the DSH frontend declares and the public site does not. Colours that are
# already covered through the raw-palette block are left out on purpose.
DSH_ALIAS = {
    "--dsw-alias-bg-document-preview": RAISED,
    "--dsw-alias-bg-document-selection": FLAT_SELECTION,
    "--dsw-alias-label-document-preview": FG,
    "--dsw-alias-label-primary-bluish": FG,
    "--dsw-alias-label-deep-diving": FG_MUTED,
    "--dsw-alias-label-deep-diving-shimmer": FG_MUTED,
    "--dsw-alias-label-shimmer": FG_MUTED,
    "--dsw-alias-link": LINK,
    "--dsw-alias-menu-group-header-fill": RAISED,
    "--dsw-alias-menu-icon": FG_MUTED,
    "--dsw-menu-surface-fill": INACTIVE,
    "--dsw-alias-switch-thumb": FG_STRONG,
    "--dsw-alias-toast-label": FG,
    "--dsw-alias-tooltip-key-bg": RAISED,
    "--dsw-alias-turn-trigger-bg": RAISED,
    "--dsw-alias-turn-trigger-bg-hover": INACTIVE,
    # One faint weight for every separator. The frontend draws 24 of them, so
    # the tone has to sit near the surface: visible as an edge, never as a line
    # competing with the text. Structure comes from the layer steps below.
    "--dsw-alias-border-l1": "#343943",
    "--dsw-alias-border-l2": "#343943",
    "--dsw-alias-border-l2-darkmode-thin": "#343943",
    "--dsw-alias-border-l3": "#343943",
    "--dsw-alias-border-l4": "#343943",
    "--dsw-alias-border-inverted": "#343943",
    "--dsw-alias-border-inverted2": "#343943",
    # Four even steps instead of the site's jumps: layer 3 lands on a full
    # line colour there, which reads heavy as a fill.
    "--dsw-alias-bg-layer-1": "#24272d",
    "--dsw-alias-bg-layer-2": "#262a31",
    "--dsw-alias-bg-layer-3": "#2a2e35",
    "--dsw-alias-bg-layer-4": "#2e323a",
    "--dsw-alias-bg-overlay": "#262a31",
    "--dsw-alias-bg-multi-select": "#2a2e35",
    "--dsw-alias-bg-module-platform": "#23272e",
    "--dsw-alias-state-idle-primary": FG_MUTED,
    "--dsw-alias-brand-primary-new-colorprimary-new-color": ACCENT,
    "--dsw-alias-code-diff-added": "rgba(152, 195, 121, .14)",
    "--dsw-alias-code-diff-deleted": "rgba(224, 108, 117, .14)",
    "--dsw-alias-file-diff-added-bg": "rgba(152, 195, 121, .08)",
    "--dsw-alias-file-diff-added-gutter": "rgba(152, 195, 121, .22)",
    "--dsw-alias-file-diff-added-marker": GREEN,
    "--dsw-alias-file-diff-deleted-bg": "rgba(224, 108, 117, .08)",
    "--dsw-alias-file-diff-deleted-gutter": "rgba(224, 108, 117, .22)",
    "--dsw-alias-file-diff-deleted-marker": RED,
}

# Settings rows end in a bare button with aria-haspopup: no fill, no border, so
# the control reads as plain text. The class names are build hashes, hence the
# attribute and suffix selectors.
CHOOSERS = """
/* Settings rows end in a bare button with aria-haspopup: no fill, no border, so
   the control reads as plain text. The class names are build hashes, hence the
   attribute and suffix selectors. */
body[data-ds-dark-theme] [class*="selector"],
body[data-ds-dark-theme] [role="dialog"] button[aria-haspopup] {
    border: 1px solid #343943;
    border-radius: var(--dsw-radius-md, 6px);
}

/* The palette section builds its chooser from the app's own Menu primitive; the
   trigger only needs the surface the app gives its own selectors. */
body[data-ds-dark-theme] .dsh-od-chooser {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    height: 36px;
    padding: 0 14px;
    border: 1px solid #343943;
    border-radius: 6px;
    background: var(--dsw-alias-bg-module-platform);
    color: var(--dsw-alias-label-primary);
    font: inherit;
    font-size: 14px;
    line-height: 20px;
    cursor: pointer;
}

body[data-ds-dark-theme] .dsh-od-chooser:hover {
    background: var(--dsw-alias-interactive-bg-hover);
}

body[data-ds-dark-theme] .dsh-od-chevron {
    flex: none;
    color: var(--dsw-alias-label-tertiary);
}
"""


# Table cells carry 10px 16px of padding from the frontend, which reads loose for
# data rows. The class name is a build hash of @deepseek-ai/dsh-client-ui-chat.
# Table decoration is applied at runtime, not baked into the stylesheet: the
# client plugin writes one of these blocks into its own style tag, chosen from
# the setting under Settings - General. "off" leaves the frontend's own table
# styling untouched.
TABLE_BASE = """
/* Selectors are plain elements: the frontend classes are build hashes. The
   first/last cell rules are restated because the frontend zeroes the outer
   padding at a higher specificity. */
body[data-ds-dark-theme] table {
    font-variant-numeric: tabular-nums;
}

/* A table's max-width is ignored while it is display: table, so the column box
   is what keeps it inside the text column: full width, always scrollable. */
body[data-ds-dark-theme] .md-table-wide {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
}

body[data-ds-dark-theme] table :is(th, td) {
    padding: 5px 12px;
    max-width: none;
}

body[data-ds-dark-theme] table :is(th:first-child, td:first-child) {
    padding-left: 12px;
}

body[data-ds-dark-theme] table :is(th:last-child, td:last-child) {
    padding-right: 12px;
}

body[data-ds-dark-theme] table th {
    font-weight: 600;
}
"""

# Table width and cell wrapping are separate choices: the width decides how far
# the table box reaches, the flow decides whether a long cell wraps or runs on.
TABLE_SIZES = {
    "full": """
body[data-ds-dark-theme] table {
    width: 100%;
    max-width: 100%;
    table-layout: auto;
}
""",
    "content": """
body[data-ds-dark-theme] table {
    width: max-content;
}
""",
}

TABLE_FLOWS = {
    "wrap": """
body[data-ds-dark-theme] table :is(th, td) {
    white-space: normal;
    overflow-wrap: anywhere;
}
""",
    "scroll": """
body[data-ds-dark-theme] table :is(th, td) {
    white-space: nowrap;
}

body[data-ds-dark-theme] table :is(th, td):only-child {
    white-space: normal;
}
""",
}

TABLE_BORDERS = {
    "grid": """
body[data-ds-dark-theme] table :is(th, td) {
    border: 1px solid #343943;
}
""",
    "rows": """
body[data-ds-dark-theme] table :is(th, td) {
    border-bottom: 1px solid #343943;
}
""",
    "none": """
body[data-ds-dark-theme] table th {
    border-bottom: 1px solid #3e4452;
}
""",
}

# after: the first data row stays flush with the header, striping starts on the
# second row (the GitHub arrangement). first: the first data row is already
# tinted. none: a flat surface.
TABLE_STRIPES = {
    "after": """
body[data-ds-dark-theme] table tbody tr:nth-child(odd) {
    background: transparent;
}

body[data-ds-dark-theme] table tbody tr:nth-child(even) {
    background: #262a31;
}
""",
    "first": """
body[data-ds-dark-theme] table tbody tr:nth-child(odd) {
    background: #262a31;
}

body[data-ds-dark-theme] table tbody tr:nth-child(even) {
    background: transparent;
}
""",
    "none": "",
}

TABLE_PARTS = {
    "base": TABLE_BASE,
    "sizes": TABLE_SIZES,
    "borders": TABLE_BORDERS,
    "stripes": TABLE_STRIPES,
    "flows": TABLE_FLOWS,
}



# Reasoning rows are rendered with the body colour, so they need their own step
# down. The class names are build hashes of @deepseek-ai/dsh-client-ui-chat.
REASONING = """
/* reasoning row: a process column under the answer */
._3GBCTG_thinkBody {
    border-left: 1px solid var(--dsw-alias-border-l3);
    padding-bottom: 14px;
}

/* Reasoning text: one grey step below the answer. The rule covers every
   descendant because the reasoning markdown does not always wrap text in <p>;
   code keeps its inline Shiki colours, links keep the brand colour. */
._3GBCTG_thinkBody :not(pre):not(code):not(a):not(.md-code-block) {
    color: color-mix(in srgb, var(--dsw-alias-label-tertiary) 65%, var(--dsw-alias-bg-base));
}

._3GBCTG_thinkBody :is(p, li) {
    line-height: 19px;
}

/* the collapsed summary line gets the same step down */
._3GBCTG_summary {
    color: color-mix(in srgb, var(--dsw-alias-label-tertiary) 78%, var(--dsw-alias-bg-base));
}
"""

# The frontend highlights code with Shiki's css-variables theme, so every token
# carries `var(--shiki-token-*)` and the palette can be set from CSS.
SHIKI = {
    "foreground": site.FG,
    "background": "transparent",
    "token-comment": site.GRAY,
    "token-keyword": site.Y["keyword"],
    "token-string": site.Y["string"],
    "token-string-expression": site.Y["string"],
    "token-constant": site.Y["numeric"],
    "token-function": site.Y["function"],
    "token-parameter": site.Y["variable"],
    "token-punctuation": site.FG,
    "token-link": site.LINK,
    "token-inserted": site.Y["diff-inserted"],
    "token-deleted": site.Y["diff-deleted"],
    "token-changed": site.Y["diff-changed"],
}


def build_css():
    out = []
    out.append("/* One Dark Pro Darker for the DSH web interface")
    out.append("   Token mapping shared with the DeepSeek web skin; the extra tokens below are")
    out.append("   declared by the DSH frontend only. Code blocks read the Shiki css-variables")
    out.append("   palette, so their token colours are set here as well. */")
    out.append("")
    out.extend(site.token_block(DSH_ALIAS, skip=set(DSH_ALIAS)))

    out.append("/* Native controls (the language select and its popup) follow the")
    out.append("   browser colour-scheme, which the app never declares, so they render")
    out.append("   light. Declaring dark keeps the popup in the theme. */")
    out.append("{} {{\n  color-scheme: dark;\n}}".format(SCOPE))
    out.append("")
    out.append("{} select {{\n  color: var(--dsw-alias-label-primary);\n  background-color: var(--dsw-alias-bg-base);\n  border: 1px solid #343943;\n  border-radius: 4px;\n  padding: 2px 8px;\n  color-scheme: dark;\n}}".format(SCOPE))
    out.append("")
    out.append("{} option {{\n  color: var(--dsw-alias-label-primary);\n  background-color: var(--dsw-alias-bg-base);\n}}".format(SCOPE))
    out.append("")
    out.append("/* The plugin fields are native selects; without an explicit border they\n   inherit the light default from the browser. */")
    out.append("{} select[class] {{\n  border: 1px solid var(--dsw-alias-border-l2);\n  border-radius: 3px;\n}}".format(SCOPE))
    out.append("")

    out.append("/* code font: same stack the editor uses on this platform */")
    out.append("{} {{\n  --ds-font-family-code: {};\n  --dsh-font-family-code: {};\n}}".format(SCOPE, CODE_FONT, CODE_FONT))
    out.append("")

    out.append("/* code block syntax: Shiki css-variables palette */")
    out.append("{} {{".format(SCOPE))
    for name, value in SHIKI.items():
        out.append("  --shiki-{}: {} !important;".format(name, value))
    out.append("}")
    out.append("")
    out.append(CHOOSERS.strip())
    out.append("")
    out.append(REASONING.strip())
    out.append("")
    return "\n".join(out)


def check_tokens(css):
    """A var() that the frontend never defines resolves to nothing, which
    silently drops the declaration."""
    known = set()
    for name in ("index.css", "tokens.css"):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        known |= set(re.findall(r"(--dsw-[a-z0-9-]+)\s*:", text))
    used = set(re.findall(r"var\((--dsw-[a-z0-9-]+)", css))
    missing = sorted(used - known)
    if missing:
        print("warning: frontend snapshot lacks " + ", ".join(missing))


def main():
    css = build_css()
    check_tokens(css)

    tables = os.path.join(HERE, "table-modes.json")
    with open(tables, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(TABLE_PARTS, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("wrote", tables)
    path = os.path.join(ROOT, "onedark.css")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(css)
        fh.write("\n")
    print("wrote", path, len(css), "bytes")


if __name__ == "__main__":
    main()
