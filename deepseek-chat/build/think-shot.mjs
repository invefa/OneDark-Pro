// Screenshot the thinking-block reproduction before and after the skin.
// Usage: node think-shot.mjs <skinCssPath>
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { BROWSER } from "./edge.mjs";

const EDGE = BROWSER;
const PORT = 9341;
const dir = import.meta.dirname;
const PROFILE = path.join(dir, "profile");
const css = fs.readFileSync(process.argv[2], "utf-8");
const page = pathToFileURL(path.join(dir, "think-demo.html")).href;

const proc = spawn(EDGE, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--hide-scrollbars",
  "--allow-file-access-from-files", "--window-size=900,620", "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target = null;
for (let i = 0; i < 80; i += 1) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    target = list.find((t) => t.type === "page");
    if (target) break;
  } catch { /* not up yet */ }
  await sleep(250);
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
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
await send("Emulation.setDeviceMetricsOverride", { width: 900, height: 620, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: page });
for (let i = 0; i < 40 && !events.includes("Page.loadEventFired"); i += 1) await sleep(200);
await sleep(500);

const probe = `(() => {
  const pick = (el, prop) => el ? getComputedStyle(el).getPropertyValue(prop).trim() : "missing";
  const think = document.querySelector(".ds-think-content .ds-markdown p");
  const answer = document.querySelector(".page > .turn > .ds-markdown p");
  const line = document.querySelector("._9ecc93a");
  return {
    thinking: pick(think, "color") + " / " + pick(think, "font-size") + " / " + pick(think, "line-height"),
    answer: pick(answer, "color") + " / " + pick(answer, "font-size") + " / " + pick(answer, "line-height"),
    rule: pick(line, "border-left-width") + " " + pick(line, "border-left-color"),
  };
})()`;

console.log("before:", JSON.stringify(await evaluate(probe)));
await shot("01-think-before.png");

await evaluate(`(() => {
  const s = document.createElement("style");
  s.id = "skin";
  s.textContent = ${JSON.stringify(css)};
  document.head.appendChild(s);
  return "ok";
})()`);
await sleep(300);

console.log("after: ", JSON.stringify(await evaluate(probe)));
await shot("02-think-after.png");

ws.close();
proc.kill();
