"""Generate the Windows Terminal schemes from the shared palette JSON.

Two schemes are emitted:

  onedark-pro-darker.json          the theme's terminal palette (terminal.ansi*)
  onedark-pro-darker-syntax.json   the editor syntax colours, for comparison

The default scheme takes the vivid terminal colours for the normal slots and
the editor syntax colours for the bright slots. The syntax variant keeps all
sixteen slots on syntax colours, for comparison.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PALETTE = os.path.join(ROOT, "onedark-pro.json")
OUT_DIR = os.path.join(ROOT, "windows-terminal")

p = json.load(open(PALETTE, encoding="utf-8"))
surface, text, syn, term, term_bright = p["surface"], p["text"], p["syntax"], p["terminal"], p["terminalBright"]


def lift(color, amount=0.12):
    raw = color.lstrip("#")
    parts = [int(raw[i:i + 2], 16) for i in (0, 2, 4)]
    lifted = [round(c + (255 - c) * amount) for c in parts]
    return "#" + "".join(f"{c:02X}" for c in lifted)


def base():
    return {
        "background": surface["bg-editor"].upper(),
        "foreground": text["fg"].upper(),
        "cursorColor": text["fg"].upper(),
        "selectionBackground": surface["line-strong"].upper(),
    }


terminal_scheme = {
    "name": "One Dark Pro Darker",
    **base(),
    "black": term["black"].upper(),
    "red": term["red"].upper(),
    "green": term["green"].upper(),
    "yellow": term["yellow"].upper(),
    "blue": term["blue"].upper(),
    "purple": term["magenta"].upper(),
    "cyan": term["cyan"].upper(),
    "white": text["fg"].upper(),
    # Bright slots carry the editor syntax colours: the terminal set made the
    # bright half look washed out next to the normal half.
    "brightBlack": syn["comment"].upper(),
    "brightRed": syn["variable"].upper(),
    "brightGreen": syn["string"].upper(),
    "brightYellow": syn["numeric"].upper(),
    "brightBlue": syn["function"].upper(),
    "brightPurple": syn["keyword"].upper(),
    "brightCyan": syn["builtin"].upper(),
    "brightWhite": "#C2CAD9",
}

# Selection in the old One Dark scheme was a light block that reads as a
# reversal of the page; Windows Terminal keeps the glyph colour, so the value
# is taken from that scheme rather than from the line grey.
terminal_scheme["selectionBackground"] = "#C2CAD9"

syntax_scheme = {
    "name": "One Dark Pro Darker Syntax",
    **base(),
    "black": term["black"].upper(),
    "red": syn["variable"].upper(),
    "green": syn["string"].upper(),
    "yellow": syn["numeric"].upper(),
    "blue": syn["function"].upper(),
    "purple": syn["keyword"].upper(),
    "cyan": syn["builtin"].upper(),
    "white": text["fg"].upper(),
    "brightBlack": syn["comment"].upper(),
    "brightRed": lift(syn["variable"]),
    "brightGreen": lift(syn["string"]),
    "brightYellow": lift(syn["numeric"]),
    "brightBlue": lift(syn["function"]),
    "brightPurple": lift(syn["keyword"]),
    "brightCyan": lift(syn["builtin"]),
    "brightWhite": "#DDDFE4",
}

def _luma(color):
    raw = color.lstrip("#")
    r, g, b = (int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


for scheme in (terminal_scheme, syntax_scheme):
    for slot in ("Black", "Red", "Green", "Yellow", "Blue", "Purple", "Cyan", "White"):
        normal, bright = scheme[slot[0].lower() + slot[1:]], scheme["bright" + slot]
        if _luma(bright) <= _luma(normal):
            print(f"warning: {scheme['name']}: bright{slot} is not brighter than {slot[0].lower() + slot[1:]}")

for filename, scheme in (
    ("onedark-pro-darker.json", terminal_scheme),
    ("onedark-pro-darker-syntax.json", syntax_scheme),
):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(scheme, fh, indent=4)
        fh.write("\n")
    print("wrote", path)
    for key, value in scheme.items():
        print(f"  {key:20} {value}")
