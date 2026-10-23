// Extract file(s) from the DSH app.asar into the workspace.
// Usage: node extract-asar.cjs <asarPath> <innerPath> <outFile>
//        node extract-asar.cjs <asarPath> --list <regex>
const fs = require("fs");

const asarPath = process.argv[2];
const target = process.argv[3];
const out = process.argv[4];

const fd = fs.openSync(asarPath, "r");
const size = fs.fstatSync(fd).size;
const probe = Buffer.alloc(Math.min(size, 16 * 1024 * 1024));
fs.readSync(fd, probe, 0, probe.length, 0);
const text = probe.toString("latin1");
const start = 16;
let depth = 0, inStr = false, esc = false, end = -1;
for (let i = start; i < text.length; i += 1) {
    const ch = text[i];
    if (inStr) {
        if (esc) esc = false;
        else if (ch === "\\") esc = true;
        else if (ch === '"') inStr = false;
        continue;
    }
    if (ch === '"') inStr = true;
    else if (ch === "{") depth += 1;
    else if (ch === "}") {
        depth -= 1;
        if (depth === 0) { end = i; break; }
    }
}
const header = JSON.parse(text.slice(start, end + 1));
const dataOffset = start + (end - start + 1);

function lookup(path) {
    let node = header;
    for (const part of path.split("/").filter(Boolean)) {
        if (!node.files || !node.files[part]) return null;
        node = node.files[part];
    }
    return node;
}

if (target === "--list") {
    const re = new RegExp(out);
    const rows = [];
    (function walk(node, prefix) {
        for (const [name, v] of Object.entries(node.files || {})) {
            const p = prefix + "/" + name;
            if (v.files) walk(v, p);
            else if (re.test(p)) rows.push([p, v.size, Number(v.offset)]);
        }
    })(header, "");
    rows.forEach(([p, s]) => console.log(p, s));
    fs.closeSync(fd);
    process.exit(0);
}

const entry = lookup(target);
if (!entry) {
    console.error("not found:", target);
    fs.closeSync(fd);
    process.exit(1);
}
if (entry.files) {
    console.error("is a directory:", target);
    fs.closeSync(fd);
    process.exit(1);
}
const buf = Buffer.alloc(entry.size);
fs.readSync(fd, buf, 0, entry.size, dataOffset + Number(entry.offset));
fs.closeSync(fd);
fs.writeFileSync(out, buf);
console.log("wrote", out, entry.size, "bytes");
