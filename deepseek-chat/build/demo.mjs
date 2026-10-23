// Screenshot demo.html with and without the skin, using the real site stylesheet.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9337;
const PROFILE = path.join(import.meta.dirname, "profile5");
const dir = import.meta.dirname;
const css = fs.readFileSync(path.join(dir, "..", "onedark-deepseek.css"), "utf-8");
const demo = pathToFileURL(path.join(dir, "demo.html")).href;

const proc = spawn(EDGE, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--hide-scrollbars",
  "--allow-file-access-from-files", "--window-size=920,820", "about:blank",
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
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}
async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(path.join(dir, name), Buffer.from(r.data, "base64"));
}

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 920, height: 820, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: demo });
for (let i = 0; i < 40 && !events.includes("Page.loadEventFired"); i += 1) await sleep(250);
await sleep(1500);

await shot("04-demo-plain.png");
await evaluate(`(() => { const s = document.createElement("style"); s.textContent = ${JSON.stringify(css)}; document.head.appendChild(s); return "ok"; })()`);
await sleep(400);
await shot("05-demo-skin.png");

console.log("font-family:", await evaluate(`getComputedStyle(document.querySelector(".md-code-block")).fontFamily`));
console.log("done");
ws.close();
proc.kill();
