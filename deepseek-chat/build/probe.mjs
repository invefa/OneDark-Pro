// Probe script: find which elements keep literal colours after the token skin.
// Usage: node probe.mjs <cssPath>

import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { BROWSER } from "./edge.mjs";

const EDGE = BROWSER;
const PORT = 9334;
const PROFILE = path.join(import.meta.dirname, "profile2");
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
  } catch { /* not up */ }
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
await sleep(2500);
await evaluate(`document.body.setAttribute("data-ds-dark-theme", ""); "ok"`);
await sleep(300);

const PROBE = `(() => {
  const rows = [];
  const seen = new Set();
  const add = (label, el) => {
    if (!el) return rows.push([label, "missing", "", ""]);
    const cs = getComputedStyle(el);
    rows.push([label, el.tagName.toLowerCase() + "." + String(el.className).split(" ").slice(0,2).join("."), cs.backgroundColor, cs.color]);
  };
  add("primary button", document.querySelector(".ds-button--primary"));
  add("text label button", document.querySelector(".ds-button--textLabelTertiary"));
  add("input field", document.querySelector("input"));
  const qr = document.querySelector("canvas,img[alt],div");
  const sheets = [...document.styleSheets].map((s) => (s.href || "inline").split("/").pop());
  const solid = [];
  for (const el of document.querySelectorAll("div,button,span,a,input")) {
    const cs = getComputedStyle(el);
    const bg = cs.backgroundColor;
    if (!bg || bg === "rgba(0, 0, 0, 0)") continue;
    if (seen.has(bg)) continue;
    seen.add(bg);
    solid.push([bg, el.tagName.toLowerCase() + "." + String(el.className).split(" ")[0]]);
  }
  return { rows, sheets, solid: solid.slice(0, 14) };
})()`;

const before = await evaluate(PROBE);
await evaluate(`(() => { const s = document.createElement("style"); s.textContent = ${JSON.stringify(css)}; document.head.appendChild(s); return "ok"; })()`);
await sleep(500);
const after = await evaluate(PROBE);

console.log("stylesheets:", JSON.stringify(before.sheets));
console.log("before rows:", JSON.stringify(before.rows, null, 1));
console.log("after rows:", JSON.stringify(after.rows, null, 1));
console.log("before bg set:", JSON.stringify(before.solid, null, 1));
console.log("after bg set:", JSON.stringify(after.solid, null, 1));

ws.close();
proc.kill();
