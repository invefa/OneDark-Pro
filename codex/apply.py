"""Merge the One Dark Pro Darker appearance settings into a Codex config.toml.

Only the keys listed below are touched; everything else in the file is kept.
A timestamped backup is written before any change.

Usage: python apply.py [path-to-config.toml]
"""

import datetime
import os
import re
import shutil
import sys

DEFAULT = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), ".codex", "config.toml")

SECTIONS = {
    "[desktop]": {
        "appearanceDarkCodeThemeId": '"one"',
    },
    "[desktop.appearanceDarkChromeTheme]": {
        "accent": '"#4d78cc"',
        "accentSource": '"custom"',
        "contrast": "60",
        "ink": '"#abb2bf"',
        "opaqueWindows": "false",
        "surface": '"#23272e"',
    },
    "[desktop.appearanceDarkChromeTheme.fonts]": {
        "code": "'\"Cascadia Code\"'",
    },
    "[desktop.appearanceDarkChromeTheme.semanticColors]": {
        "diffAdded": '"#98c379"',
        "diffRemoved": '"#e06c75"',
        "skill": '"#c162de"',
    },
}


def section_bounds(text, header):
    start = text.find(header)
    if start < 0:
        return None
    nxt = text.find("\n[", start + len(header))
    return start, (len(text) if nxt < 0 else nxt + 1)


def set_keys(text, header, values):
    bounds = section_bounds(text, header)
    if bounds is None:
        block = header + "\n" + "".join("%s = %s\n" % kv for kv in values.items()) + "\n"
        return text.rstrip("\n") + "\n\n" + block

    start, end = bounds
    block = text[start:end]
    for key, value in values.items():
        pattern = r"(?m)^" + re.escape(key) + r"\s*=\s*.*$"
        if re.search(pattern, block):
            block = re.sub(pattern, key + " = " + value, block)
        else:
            block = block.rstrip("\n") + "\n" + key + " = " + value + "\n"
    return text[:start] + block + text[end:]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.exists(path):
        print("no config at", path)
        return 1

    original = open(path, encoding="utf-8").read()
    updated = original
    for header, values in SECTIONS.items():
        updated = set_keys(updated, header, values)

    if updated == original:
        print("already up to date:", path)
        return 0

    backup = path + ".bak-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.copy2(path, backup)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(updated)
    print("updated", path)
    print("backup ", backup)
    return 0


if __name__ == "__main__":
    sys.exit(main())
