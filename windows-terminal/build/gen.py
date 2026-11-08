"""Generate the Windows Terminal scheme from the shared palette JSON.

The ANSI slots use the editor syntax colours rather than the palette's terminal
variant, so CLI output matches what the editor shows. Bright variants are the
same hues lifted towards white; bright black carries the comment grey.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PALETTE = os.path.join(ROOT, "onedark-pro.json")
OUT = os.path.join(ROOT, "windows-terminal", "onedark-pro-darker.json")

p = json.load(open(PALETTE, encoding="utf-8"))
surface, text, syn, term, term_bright = p["surface"], p["text"], p["syntax"], p["terminal"], p["terminalBright"]


def lift(color, amount=0.15):
    raw = color.lstrip("#")
    parts = [int(raw[i:i + 2], 16) for i in (0, 2, 4)]
    lifted = [round(c + (255 - c) * amount) for c in parts]
    return "#" + "".join(f"{c:02X}" for c in lifted)


scheme = {
    "name": "One Dark Pro Darker",
    "background": surface["bg-editor"].upper(),
    "foreground": text["fg"].upper(),
    "cursorColor": text["fg"].upper(),
    "selectionBackground": surface["line-strong"].upper(),
    "black": term["black"].upper(),
    "red": syn["variable"].upper(),
    "green": syn["string"].upper(),
    "yellow": syn["type"].upper(),
    "blue": syn["function"].upper(),
    "purple": syn["keyword"].upper(),
    "cyan": syn["builtin"].upper(),
    "white": term["white"].upper(),
    "brightBlack": syn["comment"].upper(),
    "brightRed": lift(syn["variable"]),
    "brightGreen": lift(syn["string"]),
    "brightYellow": lift(syn["type"]),
    "brightBlue": lift(syn["function"]),
    "brightPurple": lift(syn["keyword"]),
    "brightCyan": lift(syn["builtin"]),
    "brightWhite": term_bright["bright-white"].upper(),
}

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(scheme, fh, indent=4)
    fh.write("\n")
print("wrote", OUT)
for key, value in scheme.items():
    print(f"  {key:20} {value}")
