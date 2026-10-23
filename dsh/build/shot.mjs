// Screenshot the local reproduction before and after the override sheet.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { BROWSER } from "../../build/edge.mjs";

const EDGE = BROWSER;
const PORT = 9340;
const dir = import.meta.dirname;
const PROFILE = path.join(dir, "profile");
const override = process.argv[2];
const css = fs.readFileSync(override, "utf-8");
const demo = pathToFileURL(path.join(dir, "demo.html")).href;

const proc = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--hide-scrollbars",
    "--allow-file-access-from-files", "--window-size=900,760", "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let page = null;
for (let i = 0; i < 80; i += 1) {
    try {
        const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
        page = list.find((t) => t.type === "page");
        if (page) break;
    } catch { /* not up yet */ }
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
    if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
}
async function shot(name) {
    const r = await send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(dir, name), Buffer.from(r.data, "base64"));
}

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 900, height: 760, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: demo });
for (let i = 0; i < 40 && !events.includes("Page.loadEventFired"); i += 1) await sleep(200);
await sleep(600);

const probe = `(() => {
  const pick = (el, prop) => el ? getComputedStyle(el).getPropertyValue(prop).trim() : "missing";
  const body = document.querySelector("._3GBCTG_thinkBody");
  const answer = document.querySelector(".answer p");
  const compact = document.querySelector("._3GBCTG_thinkBody p") || document.querySelector("._compact_1ypvv_331");
  return {
    reasoningColor: pick(compact, "color"),
    reasoningSize: pick(compact, "font-size"),
    reasoningLine: pick(compact, "line-height"),
    answerColor: pick(answer, "color"),
    answerSize: pick(answer, "font-size"),
    bodyBorder: pick(body, "border-left-width") + " " + pick(body, "border-left-color"),
    bodyBottom: pick(body, "padding-bottom"),
  };
})()`;

console.log("before:", JSON.stringify(await evaluate(probe)));
await shot("01-before.png");

await evaluate(`(() => {
  const s = document.createElement("style");
  s.id = "reasoning-override";
  s.textContent = ${JSON.stringify(css)};
  document.head.appendChild(s);
  return "ok";
})()`);
await sleep(300);

console.log("after: ", JSON.stringify(await evaluate(probe)));
await shot("02-after.png");

ws.close();
proc.kill();
