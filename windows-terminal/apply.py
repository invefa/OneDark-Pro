"""Merge the One Dark Pro Darker scheme into a Windows Terminal settings.json.

The scheme is added to "schemes" (replacing a scheme with the same name) and
every "One Dark Pro" colour reference is pointed at the new scheme. A
timestamped backup is written before any change.

Usage: python apply.py [path-to-settings.json]
"""

import datetime
import json
import os
import re
import shutil
import sys

DEFAULT = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "Packages", "Microsoft.WindowsTerminal_8wekyb3d8bbwe", "LocalState", "settings.json",
)
NAME = "One Dark Pro Darker"
OLD_NAMES = ("One Dark Pro",)

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMES = [
    json.load(open(os.path.join(HERE, name), encoding="utf-8"))
    for name in sorted(os.listdir(HERE))
    if name.startswith("onedark-pro-darker") and name.endswith(".json")
]


def strip_jsonc(text):
    """Remove comments and trailing commas so the file can be parsed."""
    out = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        out.append(ch)
        i += 1
    cleaned = "".join(out)
    return re.sub(r",(\s*[}\]])", r"\1", cleaned)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.exists(path):
        print("no settings at", path)
        return 1

    raw = open(path, encoding="utf-8").read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = json.loads(strip_jsonc(raw))

    names = {scheme["name"] for scheme in SCHEMES}
    schemes = [s for s in data.get("schemes") or [] if s.get("name") not in names]
    schemes.extend(SCHEMES)
    data["schemes"] = schemes

    def rewrite(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "colorScheme":
                    if isinstance(value, str) and value in OLD_NAMES:
                        node[key] = NAME
                    elif isinstance(value, dict):
                        for slot, name in list(value.items()):
                            if name in OLD_NAMES:
                                value[slot] = NAME
                else:
                    rewrite(value)
        elif isinstance(node, list):
            for item in node:
                rewrite(item)

    rewrite(data)

    text = json.dumps(data, indent=4, ensure_ascii=False) + "\n"
    if text == raw:
        print("already up to date:", path)
        return 0

    backup = path + ".bak-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.copy2(path, backup)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("updated", path)
    print("backup ", backup)
    return 0


if __name__ == "__main__":
    sys.exit(main())
