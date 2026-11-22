"""Build an IDA Pro 9 theme from IDA's own dark theme.

IDA keeps two colour systems: the Qt stylesheet under themes/<name>/theme.css,
and the listing palette carried by qproperty-line-* inside CustomIDAMemo. This
script rewrites both by remapping the dark theme's colour literals onto One
Dark Pro Darker, so the selector structure of the shipped theme is preserved.
"""

import os
import re
import sys

PALETTE = {
    "bg": "#23272e",
    "panel": "#1e2227",
    "raised": "#2c313c",
    "line": "#3e4452",
    "dim": "#6b717d",
    "muted": "#9da5b4",
    "fg": "#abb2bf",
    "strong": "#dcdcdc",
    "comment": "#7f848e",
    "red": "#e06c75",
    "green": "#98c379",
    "yellow": "#e5c07b",
    "orange": "#d19a66",
    "blue": "#61afef",
    "purple": "#c678dd",
    "cyan": "#56b6c2",
    "accent": "#4d78cc",
    "cursor": "#528bff",
}

# Explicit roles first; everything else falls back to the grey ramp below.
EXPLICIT = {
    # chrome
    "#363636": PALETTE["bg"],
    "#2d2d2d": PALETTE["panel"],
    "#2a2a2a": PALETTE["raised"],
    "#474747": PALETTE["line"],
    "#ddd": PALETTE["fg"],
    "#666": PALETTE["dim"],
    "#666666": PALETTE["dim"],
    "#555": PALETTE["panel"],
    "#585858": PALETTE["raised"],
    "#4d4d4d": PALETTE["raised"],
    "#424242": PALETTE["raised"],
    "#4a4a4a": PALETTE["line"],
    "#444": PALETTE["panel"],
    "#333": PALETTE["panel"],
    "#111": PALETTE["panel"],
    "#242424": PALETTE["panel"],
    "#6c4634": PALETTE["orange"],
    "#0aa": PALETTE["accent"],
    "#0ee": PALETTE["blue"],
    "#077": PALETTE["accent"],
    "#aaaaaa": PALETTE["fg"],
    "#c0c0c0": PALETTE["muted"],
    "#b2b2b2": PALETTE["muted"],
    "#808080": PALETTE["dim"],
    "#606060": PALETTE["dim"],
    "#595959": PALETTE["dim"],
    "#777": PALETTE["dim"],
    # listing foregrounds
    "#ffc5f3": PALETTE["comment"],
    "#82607e": PALETTE["dim"],
    "#ebebb9": PALETTE["yellow"],
    "#ffecbb": PALETTE["yellow"],
    "#d25032": PALETTE["orange"],
    "#69d200": PALETTE["green"],
    "#00ff00": PALETTE["green"],
    "#79f300": PALETTE["green"],
    "#9dd600": PALETTE["green"],
    "#ffd200": PALETTE["blue"],
    "#ff8000": PALETTE["red"],
    "#ff4646": PALETTE["red"],
    "#ff3437": PALETTE["red"],
    "#ffaa7f": PALETTE["blue"],
    "#7c7c61": PALETTE["cyan"],
    "#808000": PALETTE["cyan"],
    "#ffaaff": PALETTE["purple"],
    "#00ffff": PALETTE["cyan"],
    "#df077e": PALETTE["purple"],
    "#ababab": PALETTE["purple"],
    "#73adad": PALETTE["cyan"],
    "#ff5afd": PALETTE["purple"],
    "#ffff7f": PALETTE["yellow"],
    "#aaff00": PALETTE["yellow"],
    "#ffff00": PALETTE["yellow"],
    "#e1ad32": PALETTE["line"],
    # graph and nav band
    "#003900": PALETTE["green"],
    "#6d0000": PALETTE["red"],
    "#0043cb": PALETTE["blue"],
    "#009100": PALETTE["green"],
    "#bc0000": PALETTE["red"],
    "#aaaaff": PALETTE["blue"],
    "#c68e00": PALETTE["orange"],
    "#f5f5f5": PALETTE["strong"],
    "#aa9f98": PALETTE["muted"],
    "#5e5854": PALETTE["dim"],
    "#00aaff": PALETTE["cyan"],
    "#ffaa00": PALETTE["yellow"],
    "#800000": PALETTE["red"],
    "#787800": PALETTE["dim"],
    "#ff00ff": PALETTE["purple"],
    "#32cd32": PALETTE["green"],
    "#4cc3fe": PALETTE["cyan"],
    "#fec34c": PALETTE["orange"],
    "#f20000": PALETTE["red"],
    "#f1f1ce": PALETTE["strong"],
    "#ecec00": PALETTE["yellow"],
    "#fe4cfe": PALETTE["purple"],
    "#6fdb6f": PALETTE["green"],
    "#ca0000": PALETTE["red"],
    "#80ff00": PALETTE["green"],
    "#00dede": PALETTE["cyan"],
    "#008000": PALETTE["green"],
    "#ff8080": PALETTE["red"],
    "#804040": PALETTE["dim"],
    "#760000": PALETTE["red"],
    "#9d9d00": PALETTE["dim"],
    "#ffff7f": PALETTE["yellow"],
    "#82607e": PALETTE["dim"],
    "#c728c7": PALETTE["purple"],
    "#ff4545": PALETTE["red"],
    "#e47251": PALETTE["orange"],
    "#5ac35a": PALETTE["green"],
    "#7171ff": PALETTE["purple"],
    "#ff7f17": PALETTE["orange"],
    "#aaaaaa": PALETTE["fg"],
}

RAMP = [
    (PALETTE["panel"], 0.05),
    (PALETTE["bg"], 0.14),
    (PALETTE["raised"], 0.20),
    (PALETTE["line"], 0.30),
    (PALETTE["dim"], 0.45),
    (PALETTE["comment"], 0.52),
    (PALETTE["muted"], 0.62),
    (PALETTE["fg"], 0.72),
    (PALETTE["strong"], 0.88),
]


def luma(hex_color):
    raw = hex_color.lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    r, g, b = (int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def nearest_grey(hex_color):
    target = luma(hex_color)
    return min(RAMP, key=lambda item: abs(item[1] - target))[0]


def remap(theme_css):
    def replace(match):
        original = match.group(0)
        key = original.lower()
        if key in EXPLICIT:
            return EXPLICIT[key]
        return nearest_grey(original)

    return re.sub(r"#[0-9a-fA-F]{3,8}\b", replace, theme_css)


LISTING_FIXES = {
    "line-bg-default": "#23272e",
    "line-bg-selected": "#3e4452",
    "line-bg-highlight": "rgba(44, 49, 60, 0.86)",
    "caret": "#528bff",
}


def fix_listing(block):
    """The dark theme's listing background is a step darker than the editor."""
    for name, value in LISTING_FIXES.items():
        block = re.sub(
            r"(qproperty-" + name + r"\s*:\s*)[^;]+;",
            lambda m, v=value: m.group(1) + v + ";",
            block,
        )
    return block


def locate_ida():
    candidates = [
        os.environ.get("IDADIR"),
        r"D:\Applications\IDA\Pro\9.0",
        r"C:\Program Files\IDA Pro 9.0",
    ]
    for path in candidates:
        if path and os.path.isfile(os.path.join(path, "themes", "dark", "theme.css")):
            return path
    return None


def main():
    ida = locate_ida()
    if not ida:
        print("IDA installation not found; set IDADIR")
        return 1
    source = os.path.join(ida, "themes", "dark", "theme.css")
    text = open(source, encoding="utf-8").read()

    text = text.replace(
        "This theme is based on the 'idaskins-dark' theme found\n  at <https://github.com/zyantific/IDASkins.git>",
        "One Dark Pro Darker. Rewritten from the shipped dark theme;\n  the selector structure comes from IDASkins.",
    )
    body = remap(text)
    raw_block = re.search(r"CustomIDAMemo\s*\{.*?\n\}", body, re.S)
    if not raw_block:
        print("CustomIDAMemo block not found")
        return 1
    fixed_block = fix_listing(raw_block.group(0))
    body = body.replace(raw_block.group(0), fixed_block)

    header = "/* Generated by ida/build/gen.py from the IDA dark theme. */\n\n"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    out = os.path.join(root, "onedark-pro-darker", "theme.css")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + body)
    print("wrote", out, len(body), "chars")

    # Listing-only variant: the shipped dark theme keeps the interface, only
    # the disassembly view takes the One Dark colours.
    block = type("M", (), {"group": staticmethod(lambda _i: fixed_block)})()
    listing = (
        header
        + "/* Listing variant: the shipped dark theme covers the interface, the\n"
        + "   disassembly view takes the One Dark colours. */\n\n"
        + '@importtheme "dark";\n\n'
        + block.group(0)
        + "\n"
    )
    dark_defs = set(re.findall(r"@def\s+([a-z0-9_]+)", text))
    missing = sorted(set(re.findall(r"\$\{([a-z0-9_]+)\}", listing)) - dark_defs)
    if missing:
        print("undefined variables:", missing)
        return 1
    out2 = os.path.join(root, "onedark-pro-darker-listing", "theme.css")
    os.makedirs(os.path.dirname(out2), exist_ok=True)
    with open(out2, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(listing)
    print("wrote", out2, len(listing), "chars")
    return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
