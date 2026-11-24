// Load the built client bundle against a stubbed DOM and check the stylesheet,
// the table decoration modes, and the settings row registration.
import fs from "node:fs";
import path from "node:path";

const here = import.meta.dirname;
const file = path.join(path.dirname(here), "plugin", "lib", "client.js");
const source = fs.readFileSync(file, "utf-8");

const styles = [];

const document = {
    head: {
        appendChild(node) {
            styles.push(node);
            return node;
        },
    },
    createElement(tag) {
        return { tag, dataset: {}, textContent: "" };
    },
    querySelector(selector) {
        const byId = /data-plugin-css="([^"]+)"/.exec(selector);
        if (byId) return styles.find((s) => s.dataset.pluginCss === byId[1]) || null;
        if (selector === "style[data-onedark-table]") {
            return styles.find((s) => Object.prototype.hasOwnProperty.call(s.dataset, "onedarkTable")) || null;
        }
        return null;
    },
};

const store = new Map();
const window = {
    __ModuleLoader__: { load(entry) { registered = entry; } },
    localStorage: {
        getItem: (key) => (store.has(key) ? store.get(key) : null),
        setItem: (key, value) => { store.set(key, String(value)); },
    },
};
let registered = null;

const React = {
    createElement: (type, props, ...children) => ({ type, props: { ...(props || {}), children: children.length === 1 ? children[0] : children } }),
    useState: (initial) => [initial, () => {}],
};
const requireStub = (name) => {
    if (name === "react") return React;
    throw new Error("unexpected module: " + name);
};

const run = new Function("window", "document", source);
run(window, document);

if (!registered) throw new Error("plugin did not register with the module loader");
if (registered.id !== "dsh-onedark") throw new Error("unexpected plugin id: " + registered.id);

const exportsObj = registered.factory(requireStub);
if (typeof exportsObj.apply !== "function") throw new Error("missing apply export");

// the settings row is registered once the slot service shows up
let slotSpec = null;
let slotComponent = null;
const ctx = {
    inject(deps, callback) {
        if (JSON.stringify(deps) !== JSON.stringify(["slots"])) {
            throw new Error("unexpected inject deps: " + JSON.stringify(deps));
        }
        callback({
            slots: {
                inject(name, register) {
                    if (name !== "settings.general.item") throw new Error("unexpected slot: " + name);
                    register();
                },
                register(spec, component) { slotSpec = spec; slotComponent = component; return () => {}; },
            },
        });
    },
};

exportsObj.apply(ctx);

if (styles.length !== 2) throw new Error("expected two stylesheets, got " + styles.length);
const sheet = styles.find((s) => s.dataset.pluginCss === "dsh-onedark/onedark.css");
const table = styles.find((s) => Object.prototype.hasOwnProperty.call(s.dataset, "onedarkTable"));
if (!sheet) throw new Error("missing the colour stylesheet");
if (!table) throw new Error("missing the table stylesheet");

if (!sheet.textContent.includes("_3GBCTG_thinkBody")) throw new Error("stylesheet lost the reasoning rule");
if (!sheet.textContent.includes("--dsw-alias-bg-base")) throw new Error("stylesheet lost the token block");
if (sheet.textContent.includes("table tbody tr:nth-child(odd)")) {
    throw new Error("table rules must stay out of the colour stylesheet");
}

if (!table.textContent.includes("table tbody tr:nth-child(odd)")) {
    throw new Error("default table mode is missing the stripe");
}
if (!table.textContent.includes("1px solid #343943")) {
    throw new Error("default table mode is missing the cell border");
}

// second apply must not stack duplicates
exportsObj.apply(ctx);
if (styles.length !== 2) throw new Error("plugin injected a duplicate stylesheet");

if (!slotSpec || slotSpec.id !== "onedark-table-style") {
    throw new Error("settings row did not register");
}
if (slotSpec.name !== "settings.general.item") {
    throw new Error("settings row registered on the wrong slot");
}

// render the settings row once so a broken component fails here, not in the page
if (typeof slotComponent !== "function") throw new Error("settings row component missing");
const tree = slotComponent();
const seen = [];
const walk = (node) => {
    if (node === null || node === undefined) return;
    if (Array.isArray(node)) { node.forEach(walk); return; }
    if (typeof node !== "object") return;
    seen.push(node.type);
    if (node.props && node.props.children !== undefined) walk(node.props.children);
};
walk(tree);
if (!seen.includes("select")) throw new Error("settings row has no select");
const selectNode = (function find(node) {
    if (node === null || node === undefined) return null;
    if (Array.isArray(node)) { for (const n of node) { const r = find(n); if (r) return r; } return null; }
    if (typeof node !== "object") return null;
    if (node.type === "select") return node;
    return node.props && node.props.children !== undefined ? find(node.props.children) : null;
})(tree);
const options = React.createElement === undefined ? [] : [];
const selectChildren = selectNode.props.children || [];
if (selectChildren.length !== 5) throw new Error("expected 5 table modes, got " + selectChildren.length);
if (selectNode.props.value !== "github") throw new Error("default mode should be github");

console.log("ok: 2 stylesheets, table mode github, settings row on settings.general.item");
console.log("colour css bytes:", sheet.textContent.length, "| table css bytes:", table.textContent.length);
