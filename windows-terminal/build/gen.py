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


def base():
    return {
        "background": surface["bg-editor"].upper(),
        "foreground": text["fg"].upper(),
        "cursorColor": text["fg"].upper(),
        "selectionBackground": "#C2CAD9",
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
    # Bright slots take the terminal scheme's normal colours: they are more
    # saturated than the lifted syntax colours and carry the emphasis better.
    "brightBlack": syn["comment"].upper(),
    "brightRed": term["red"].upper(),
    "brightGreen": term["green"].upper(),
    "brightYellow": term["yellow"].upper(),
    "brightBlue": term["blue"].upper(),
    "brightPurple": term["magenta"].upper(),
    "brightCyan": term["cyan"].upper(),
    "brightWhite": term["white"].upper(),
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
