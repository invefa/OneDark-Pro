"""Generate the OpenCode theme from the shared palette JSON."""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PALETTE = os.path.join(ROOT, "onedark-pro.json")
OUT = os.path.join(ROOT, "opencode", "onedark-pro-darker.json")

p = json.load(open(PALETTE, encoding="utf-8"))
surface, text, accent, status, syn = p["surface"], p["text"], p["accent"], p["status"], p["syntax"]

DEFS = {
    "bg": surface["bg-editor"],
    "bgPanel": surface["bg-sidebar"],
    "bgElement": surface["bg-raised"],
    "bgCode": surface["bg-input"],
    "line": surface["line-strong"],
    "lineSoft": surface["bg-inactive"],
    "lineStrong": text["fg-faint"],
    "fg": text["fg"],
    "fgStrong": text["fg-strong"],
    "fgMuted": text["fg-muted"],
    "fgDim": text["fg-dim"],
    "accent": accent["accent"],
    "link": accent["link"],
    "cursor": accent["cursor"],
    "red": syn["variable"],
    "purple": syn["keyword"],
    "blue": syn["function"],
    "cyan": syn["builtin"],
    "green": syn["string"],
    "orange": syn["numeric"],
    "yellow": syn["type"],
    "comment": syn["comment"],
    "added": status["added"],
    "removed": status["deleted"],
    "diffAddedBg": "#1f2a24",
    "diffRemovedBg": "#2c2327",
}

# dark and light point at the same values: the palette only defines a dark
# variant, and OpenCode requires both slots.
THEME = {
    "primary": ("link", "link"),
    "secondary": ("cyan", "cyan"),
    "accent": ("purple", "purple"),
    "error": ("red", "red"),
    "warning": ("yellow", "yellow"),
    "success": ("green", "green"),
    "info": ("cyan", "cyan"),
    "text": ("fg", "fg"),
    "textMuted": ("comment", "comment"),
    "background": ("bg", "bg"),
    "backgroundPanel": ("bgPanel", "bgPanel"),
    "backgroundElement": ("bgElement", "bgElement"),
    "border": ("line", "line"),
    "borderActive": ("lineStrong", "lineStrong"),
    "borderSubtle": ("lineSoft", "lineSoft"),
    "diffAdded": ("green", "green"),
    "diffRemoved": ("red", "red"),
    "diffContext": ("comment", "comment"),
    "diffHunkHeader": ("link", "link"),
    "diffHighlightAdded": ("green", "green"),
    "diffHighlightRemoved": ("red", "red"),
    "diffAddedBg": ("diffAddedBg", "diffAddedBg"),
    "diffRemovedBg": ("diffRemovedBg", "diffRemovedBg"),
    "diffContextBg": ("bg", "bg"),
    "diffLineNumber": ("fgFaint" if "fgFaint" in DEFS else "fgDim", "fgDim"),
    "diffAddedLineNumberBg": ("diffAddedBg", "diffAddedBg"),
    "diffRemovedLineNumberBg": ("diffRemovedBg", "diffRemovedBg"),
    "markdownText": ("fg", "fg"),
    "markdownHeading": ("fgStrong", "fgStrong"),
    "markdownLink": ("link", "link"),
    "markdownLinkText": ("link", "link"),
    "markdownCode": ("green", "green"),
    "markdownBlockQuote": ("comment", "comment"),
    "markdownEmph": ("orange", "orange"),
    "markdownStrong": ("fgStrong", "fgStrong"),
    "markdownHorizontalRule": ("line", "line"),
    "markdownListItem": ("fg", "fg"),
    "markdownListEnumeration": ("purple", "purple"),
    "markdownImage": ("link", "link"),
    "markdownImageText": ("fgMuted", "fgMuted"),
    "markdownCodeBlock": ("green", "green"),
    "syntaxComment": ("comment", "comment"),
    "syntaxKeyword": ("purple", "purple"),
    "syntaxFunction": ("blue", "blue"),
    "syntaxVariable": ("red", "red"),
    "syntaxString": ("green", "green"),
    "syntaxNumber": ("orange", "orange"),
    "syntaxType": ("yellow", "yellow"),
    "syntaxOperator": ("cyan", "cyan"),
    "syntaxPunctuation": ("fg", "fg"),
}

theme = {}
for key, (dark, light) in THEME.items():
    theme[key] = {"dark": dark, "light": light}

doc = {
    "$schema": "https://opencode.ai/theme.json",
    "defs": DEFS,
    "theme": theme,
}

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
print("wrote", OUT, len(json.dumps(doc)), "bytes")
