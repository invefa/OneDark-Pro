"""Pull the runtime-injected stylesheets out of a DSH client bundle.

Each client plugin embeds its CSS as a string and injects it as
<style data-plugin-css="<package>/<File>.module.css">. Reversing that gives the
exact rules the running UI uses, including the hashed class names.
"""

import json
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

js = src.read_text(encoding="utf-8", errors="replace")

# const css$9 = "...";  followed by the tag id
pattern = re.compile(r'const\s+css\$?\d*\s*=\s*("(?:[^"\\]|\\.)*")\s*;', re.S)
tags = re.findall(r'const tagId\$?\d*\s*=\s*"([^"]+)"', js)

found = []
for m in pattern.finditer(js):
    try:
        text = json.loads(m.group(1))
    except json.JSONDecodeError:
        continue
    if len(text) < 40 or "{" not in text:
        continue
    tail = js[m.end():m.end() + 400]
    tag = re.search(r'const tagId\$?\d* = "([^"]+)"', tail)
    name = tag.group(1) if tag else None
    found.append((name, text))

print("stylesheets found:", len(found))
for name, text in found:
    stem = (name or "unnamed").split("/")[-1].replace(".module.css", "").replace(".css", "")
    path = out_dir / f"{stem}.css"
    path.write_text(text, encoding="utf-8")
    print(f"  {stem}.css {len(text)} bytes  <- {name}")
    # list the hashed classes so the override sheet can be written against them
    classes = sorted(set(re.findall(r"\.(_[A-Za-z0-9]+_[0-9a-z]{4,8})", text)))
    if classes:
        print("     classes:", " ".join(classes[:12]), "..." if len(classes) > 12 else "")
