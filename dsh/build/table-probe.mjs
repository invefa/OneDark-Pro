// Read the computed table styles in a headless page.
import { spawn } from "node:child_process";
import path from "node:path";
import { BROWSER } from "../../build/edge.mjs";

const PORT = 9377;
const PROFILE = path.join(import.meta.dirname, "profile-table");
const PAGE = "file:///" + path.join(import.meta.dirname, "table-demo.html").replace(/\\/g, "/");

const proc = spawn(BROWSER, [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`,
    "--allow-file-access-from-files",
    "--disable-gpu",
    "--no-first-run",
    PAGE,
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target = null;
for (let i = 0; i < 80; i += 1) {
    try {
        const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
        target = list.find((t) => t.type === "page" && t.url.includes("table-demo"));
        if (target) break;
    } catch { /* not up yet */ }
    await sleep(250);
}
if (!target) {
    console.log("no page target");
    proc.kill();
    process.exit(1);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res, rej) => {
    ws.addEventListener("open", res, { once: true });
    ws.addEventListener("error", rej, { once: true });
});
let seq = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
        const p = pending.get(m.id);
        pending.delete(m.id);
        if (m.error) p.reject(new Error(JSON.stringify(m.error))); else p.resolve(m.result);
    }
});
const send = (method, params = {}) => {
    seq += 1;
    ws.send(JSON.stringify({ id: seq, method, params }));
    return new Promise((resolve, reject) => pending.set(seq, { resolve, reject }));
};

await sleep(800);

const expr = `(() => {
    const table = document.querySelector("table");
    const tables = [...document.querySelectorAll("table")];
    const cell = document.querySelectorAll("table")[1] ? document.querySelectorAll("table")[1].querySelector("td") : null;
    const wrap = document.querySelector("._tableScroll_13jw0_199");
    const pick = (el, props) => {
        if (!el) return null;
        const cs = getComputedStyle(el);
        const out = {};
        for (const p of props) out[p] = cs.getPropertyValue(p);
        out.rect = Math.round(el.getBoundingClientRect().width) + "x" + Math.round(el.getBoundingClientRect().height);
        out.scrollWidth = el.scrollWidth;
        return out;
    };
    return {
        tables: tables.map((el) => pick(el, ["width", "max-width"])),
        lastCell: pick(cell, ["white-space", "width"]),
        onlyChild: cell ? cell.matches(":only-child") : null,
        siblings: cell && cell.parentElement ? cell.parentElement.children.length : null,
        ruleHit: cell ? cell.matches("body[data-ds-dark-theme] table :is(th, td):only-child") : null,
        wrap: pick(wrap, ["display", "width", "max-width", "overflow-x"]),
        cell: pick(cell, ["width", "white-space", "word-break", "overflow-wrap", "padding"]),
    };
})()`;

const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
console.log(JSON.stringify(r.result.value, null, 2));
ws.close();
proc.kill();
