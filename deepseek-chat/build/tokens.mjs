// Verify prism token colours inside the real stylesheet context.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { BROWSER } from "./edge.mjs";

const EDGE = BROWSER;
const PORT = 9335;
const PROFILE = path.join(import.meta.dirname, "profile3");
const css = fs.readFileSync(process.argv[2], "utf-8");

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
    if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
    return r.result.value;
}

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: "https://chat.deepseek.com/" });
for (let i = 0; i < 60 && !events.includes("Page.loadEventFired"); i += 1) await sleep(250);
await sleep(2000);
await evaluate(`document.body.setAttribute("data-ds-dark-theme", ""); "ok"`);
await evaluate(`(() => { const s = document.createElement("style"); s.textContent = ${JSON.stringify(css)}; document.head.appendChild(s); return "ok"; })()`);
await sleep(300);

const RESULT = `(() => {
  const pre = document.createElement("pre");
  pre.className = "md-code-block md-code-block-dark";
  pre.innerHTML = '<code class="language-javascript">' +
    ['keyword', 'string', 'comment', 'number', 'function', 'class-name', 'variable', 'builtin', 'property', 'operator', 'punctuation']
      .map((c) => '<span class="token ' + c + '">' + c + '</span>').join(" ") + '</code>';
  document.body.appendChild(pre);
  const out = {};
  for (const span of pre.querySelectorAll(".token")) {
    const cs = getComputedStyle(span);
    out[span.className.replace("token ", "")] = cs.color;
  }
  out["__pre-background"] = getComputedStyle(pre).backgroundColor;
  out["__code-color"] = getComputedStyle(pre.querySelector("code")).color;
  pre.remove();
  return out;
})()`;

console.log(JSON.stringify(await evaluate(RESULT), null, 1));
ws.close();
proc.kill();
