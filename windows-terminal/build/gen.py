"""Generate the Windows Terminal schemes from the shared palette JSON.

Two schemes are emitted:

  onedark-pro-darker.json          the theme's terminal palette (terminal.ansi*)
  onedark-pro-darker-syntax.json   the editor syntax colours, for comparison

The terminal palette is the default; the syntax variant exists because editor
colours are tuned for sparse highlighting and read pale on a full screen of
output, so it is useful to switch between them and judge.
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
    "white": term["white"].upper(),
    "brightBlack": term_bright["bright-black"].upper(),
    "brightRed": term_bright["bright-red"].upper(),
    "brightGreen": term_bright["bright-green"].upper(),
    "brightYellow": term_bright["bright-yellow"].upper(),
    "brightBlue": term_bright["bright-blue"].upper(),
    "brightPurple": term_bright["bright-magenta"].upper(),
    "brightCyan": term_bright["bright-cyan"].upper(),
    "brightWhite": term_bright["bright-white"].upper(),
}

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
