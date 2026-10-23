// Headless Edge + CDP driver used to verify the skin against the live site.
// Usage: node shot.mjs <cssPath> <outDir>

import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { BROWSER } from "../../build/edge.mjs";

const EDGE = BROWSER;
const PORT = 9333;
const PROFILE = path.join(import.meta.dirname, "profile");
const cssPath = process.argv[2];
const outDir = process.argv[3] || import.meta.dirname;

const css = fs.readFileSync(cssPath, "utf-8");

const proc = spawn(EDGE, [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-gpu",
    "--hide-scrollbars",
    "--window-size=1280,900",
    "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function jsonList() {
    const res = await fetch(`http://127.0.0.1:${PORT}/json/list`);
    return res.json();
}

let page = null;
for (let i = 0; i < 80; i += 1) {
    try {
        const list = await jsonList();
        page = list.find((t) => t.type === "page");
        if (page) break;
    } catch {
        // browser not up yet
    }
    await sleep(250);
}
if (!page) throw new Error("no page target");

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
});

let seq = 0;
const pending = new Map();
const events = [];
ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
        const { resolve, reject } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result);
    } else if (msg.method) {
        events.push(msg.method);
    }
});

function send(method, params = {}) {
    seq += 1;
    const id = seq;
    ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

async function evaluate(expression) {
    const res = await send("Runtime.evaluate", {
        expression,
        returnByValue: true,
        awaitPromise: true,
    });
    if (res.exceptionDetails) throw new Error(JSON.stringify(res.exceptionDetails));
    return res.result.value;
}

async function shot(name) {
    const res = await send("Page.captureScreenshot", { format: "png" });
    const file = path.join(outDir, name);
    fs.writeFileSync(file, Buffer.from(res.data, "base64"));
    return file;
}

const READ_COLORS = `(() => {
  const cs = getComputedStyle(document.body);
  const root = getComputedStyle(document.documentElement);
  const pick = (el, prop) => {
    const s = getComputedStyle(el);
    return s.getPropertyValue(prop).trim() || s[prop];
  };
  const probe = document.createElement("div");
  probe.style.background = "var(--dsw-alias-bg-base)";
  probe.style.color = "var(--dsw-alias-label-primary)";
  document.body.appendChild(probe);
  const ps = getComputedStyle(probe);
  const out = {
    bodyBg: cs.backgroundColor,
    tokenBgBase: ps.backgroundColor,
    tokenLabelPrimary: ps.color,
    tokenSidebar: (() => {
      probe.style.background = "var(--dsw-specific-sidebar-fill)";
      return getComputedStyle(probe).backgroundColor;
    })(),
    tokenCodeBlock: (() => {
      probe.style.background = "var(--dsw-alias-markdown-code-block)";
      return getComputedStyle(probe).backgroundColor;
    })(),
    darkAttr: document.body.hasAttribute("data-ds-dark-theme"),
  };
  probe.remove();
  return out;
})()`;

const MOCK = `(() => {
  const wrap = document.createElement("div");
  wrap.id = "odp-mock";
  wrap.style.cssText = "position:fixed;left:0;right:0;bottom:0;z-index:2147483647;padding:18px 40px 26px;" +
    "background:var(--dsw-alias-bg-base);border-top:1px solid var(--dsw-alias-border-l2);max-height:60vh;overflow:auto";
  const t = (cls, text) => '<span class="token ' + cls + '">' + text + '</span>';
  const code = [
    t("keyword", "const") + " " + t("function", "render") + t("punctuation", "(") +
      t("parameter", "items") + t("punctuation", ")") + " " + t("operator", "=&gt;") + " " + t("punctuation", "{"),
    "&#160;&#160;" + t("keyword", "return") + " " + t("variable", "items") + t("punctuation", ".") +
      t("property", "map") + t("punctuation", "(") + t("parameter", "item") + t("punctuation", " =&gt; ") +
      t("string", "\\"hi\\"") + t("punctuation", ")") + t("punctuation", ";"),
    "&#160;&#160;" + t("comment", "// 42 is a constant, log is builtin"),
    t("punctuation", "}") + t("punctuation", ";") + " " + t("class-name", "Widget") + t("punctuation", ".")
      + t("builtin", "log") + t("punctuation", "(") + t("number", "42") + t("punctuation", ")"),
  ].join("<br>");
  wrap.innerHTML =
    '<div class="ds-markdown" style="max-width:780px">' +
      '<p>Answer body with <strong>bold</strong>, <em>italic</em>, an <a href="#">inline link</a> and <code>inline_code()</code>.</p>' +
      '<ul><li>First list item</li><li>Second list item</li></ul>' +
      '<pre class="md-code-block md-code-block-dark" style="padding:12px 14px;border-radius:4px;overflow:auto;white-space:pre">' +
        '<code class="language-javascript">' + code + '</code></pre>' +
      '<blockquote><p>A quoted line</p></blockquote>' +
    '</div>';
  const codeEl = wrap.querySelector("code");
  if (codeEl) codeEl.style.whiteSpace = "pre";
  document.body.appendChild(wrap);
  return "ok";
})()`;

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", {
  width: 1280, height: 900, deviceScaleFactor: 1, mobile: false,
});

await send("Page.navigate", { url: "https://chat.deepseek.com/" });
for (let i = 0; i < 60 && !events.includes("Page.loadEventFired"); i += 1) {
  await sleep(250);
}
await sleep(2500);

// DeepSeek stores its theme choice; force the dark attribute the skin targets.
await evaluate(`document.body.setAttribute("data-ds-dark-theme", ""); "ok"`);
await sleep(400);

const before = await evaluate(READ_COLORS);
await shot("01-before.png");

await evaluate(`(() => {
  const s = document.createElement("style");
  s.id = "odp-skin";
  s.textContent = ${JSON.stringify(css)};
  document.head.appendChild(s);
  return "injected";
})()`);
await sleep(600);

const after = await evaluate(READ_COLORS);
await shot("02-after.png");

await evaluate(MOCK);
await sleep(400);
await shot("03-markdown.png");

fs.writeFileSync(path.join(outDir, "colors.json"), JSON.stringify({ before, after }, null, 2));
console.log(JSON.stringify({ before, after }, null, 2));

ws.close();
proc.kill();
