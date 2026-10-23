// Load the userscript into the live page and check both the dark-mode path
// and the "wait for dark theme" path.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { BROWSER } from "../../build/edge.mjs";

const EDGE = BROWSER;
const PORT = 9336;
const PROFILE = path.join(import.meta.dirname, "profile4");
const source = fs.readFileSync(process.argv[2], "utf-8");

const proc = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--window-size=1280,900", "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let page = null;
for (let i = 0; i < 80; i += 1) {
    try {
        const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
        page = list.find((t) => t.type === "page");
        if (page) break;
    } catch { /* wait */ }
    await sleep(250);
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => {
    ws.addEventListener("open", res, { once: true });
    ws.addEventListener("error", rej, { once: true });
});
let seq = 0;
const pending = new Map();
const events = [];
ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
        const { resolve, reject } = pending.get(m.id);
        pending.delete(m.id);
        if (m.error) reject(new Error(JSON.stringify(m.error))); else resolve(m.result);
    } else if (m.method) events.push(m.method);
});
const send = (method, params = {}) => {
    seq += 1;
    ws.send(JSON.stringify({ id: seq, method, params }));
    return new Promise((resolve, reject) => pending.set(seq, { resolve, reject }));
};
async function evaluate(expression) {
    const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) return { error: JSON.stringify(r.exceptionDetails).slice(0, 300) };
    return r.result.value;
}

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: "https://chat.deepseek.com/" });
for (let i = 0; i < 60 && !events.includes("Page.loadEventFired"); i += 1) await sleep(250);
await sleep(2000);

const STATE = `(() => ({
  style: !!document.getElementById("onedark-pro-darker"),
  bodyBg: getComputedStyle(document.body).backgroundColor,
  dark: document.body.hasAttribute("data-ds-dark-theme")
}))()`;

// 1. dark mode already active
await evaluate(`document.body.setAttribute("data-ds-dark-theme", ""); "ok"`);
await sleep(200);
console.log("dark mode, before script:", JSON.stringify(await evaluate(STATE)));
console.log("run script:", JSON.stringify(await evaluate(source)));
await sleep(400);
console.log("dark mode, after script:", JSON.stringify(await evaluate(STATE)));

// 2. light mode: script must hold off until the attribute appears
await evaluate(`(() => {
  const s = document.getElementById("onedark-pro-darker");
  if (s) s.remove();
  document.body.removeAttribute("data-ds-dark-theme");
  return "reset";
})()`);
console.log("light mode, before script:", JSON.stringify(await evaluate(STATE)));
console.log("run script:", JSON.stringify(await evaluate(source)));
await sleep(400);
console.log("light mode, after script (expect no style):", JSON.stringify(await evaluate(STATE)));
await evaluate(`document.body.setAttribute("data-ds-dark-theme", ""); "ok"`);
await sleep(400);
console.log("switched to dark later (expect style):", JSON.stringify(await evaluate(STATE)));

ws.close();
proc.kill();
