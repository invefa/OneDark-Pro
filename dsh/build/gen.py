"""Generate the One Dark Pro Darker skin for the DSH web interface.

The palette mapping lives in the DeepSeek web skin because both surfaces use the
same `--dsw-*` design tokens; this generator loads that module and reuses its
`token_block()`, then adds the tokens DSH declares on top plus the reasoning rules.
"""

import importlib.util
import os

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

# Table cells carry 10px 16px of padding from the frontend, which reads loose for
# data rows. The class name is a build hash of @deepseek-ai/dsh-client-ui-chat.
TABLE = """
body[data-ds-dark-theme] ._tableScroll_1ypvv_192 :is(th, td) {
    padding: 5px 12px;
}
"""


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
    out.extend(site.token_block(DSH_ALIAS))

    out.append("/* Native controls (the language select and its popup) follow the")
    out.append("   browser colour-scheme, which the app never declares, so they render")
    out.append("   light. Declaring dark keeps the popup in the theme. */")
    out.append("{} {{\n  color-scheme: dark;\n}}".format(SCOPE))
    out.append("")
    out.append("{} select,\n{} option {{\n  color: var(--dsw-alias-label-primary);\n  background-color: var(--dsw-alias-bg-base);\n  color-scheme: dark;\n}}".format(SCOPE, SCOPE))
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
    out.append(TABLE.strip())
    out.append("")
    out.append(REASONING.strip())
    out.append("")
    return "\n".join(out)


def main():
    css = build_css()
    path = os.path.join(ROOT, "onedark.css")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(css)
        fh.write("\n")
    print("wrote", path, len(css), "bytes")


if __name__ == "__main__":
    main()
