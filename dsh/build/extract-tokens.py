"""Pull the design-token CSS text out of the DSH theme client bundle."""
import json
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
js = src.read_text(encoding="utf-8", errors="replace")

blocks = []
for m in re.finditer(r'("(?:[^"\\]|\\.)*")', js):
    raw = m.group(1)
    if "--dsw-alias-bg-base" not in raw and "--dsw-static-neutral-bluish-950" not in raw:
        continue
    try:
        text = json.loads(raw)
    except json.JSONDecodeError:
        continue
    blocks.append(text)

print("blocks:", len(blocks))
merged = "\n".join(blocks)
out.write_text(merged, encoding="utf-8")
print("wrote", out, len(merged), "bytes")

for token in ("--dsw-alias-label-primary", "--dsw-alias-label-secondary",
              "--dsw-alias-label-tertiary", "--dsw-alias-label-caption",
              "--dsw-alias-bg-base", "--dsw-alias-border-l2"):
    vals = sorted(set(re.findall(re.escape(token) + r"\s*:\s*([^;}]+)", merged)))
    print(" ", token, "->", vals)
