"""Generate the Windows Terminal scheme from the shared palette JSON.

The ANSI slots use the palette's terminal variant. One Dark Pro keeps a
separate, slightly darker set for terminals; the editor syntax colours are
pastel by comparison and read washed out in a full screen of output.
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

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(scheme, fh, indent=4)
    fh.write("\n")
print("wrote", OUT)
for key, value in scheme.items():
    print(f"  {key:20} {value}")
