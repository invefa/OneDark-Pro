// Load the built client bundle against a stubbed DOM: stylesheet injection,
// table decoration axes, and the palette settings section.
import fs from "node:fs";
import path from "node:path";

const here = import.meta.dirname;
const file = path.join(path.dirname(here), "plugin", "lib", "client.js");
const source = fs.readFileSync(file, "utf-8");

const styles = [];
const document = {
    head: { appendChild(node) { styles.push(node); return node; } },
    createElement(tag) { return { tag, dataset: {}, textContent: "" }; },
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
let registered = null;
const window = {
    __ModuleLoader__: { load(entry) { registered = entry; } },
    localStorage: {
        getItem: (key) => (store.has(key) ? store.get(key) : null),
        setItem: (key, value) => { store.set(key, String(value)); },
        removeItem: (key) => { store.delete(key); },
    },
};

const React = {
    createElement: (type, props, ...children) => {
        const merged = { ...(props || {}), children: children.length === 1 ? children[0] : children };
        // expand function components so the walk sees their real output
        if (typeof type === "function") return type(merged);
        return { type, props: merged };
    },
    useState: (initial) => [initial, () => {}],
};
const requireStub = (name) => {
    if (name === "react") return React;
    throw new Error("unexpected module: " + name);
};

const run = new Function("window", "document", source);
run(window, document);

if (!registered) throw new Error("plugin did not register with the module loader");
if (registered.id !== "dsh-onedark") throw new Error("unexpected plugin id");

const exportsObj = registered.factory(requireStub);
if (typeof exportsObj.apply !== "function") throw new Error("missing apply export");

let sectionSpec = null;
let sectionComponent = null;
const ctx = {
    inject(deps, callback) {
        if (JSON.stringify(deps) !== JSON.stringify(["slots"])) throw new Error("unexpected deps");
        callback({
            slots: {
                inject(name, register) {
                    if (name !== "settings.section") throw new Error("unexpected slot: " + name);
                    register();
                },
                register(spec, component) {
                    sectionSpec = spec;
                    sectionComponent = component;
                    return () => {};
                },
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
if (!sheet.textContent.includes("--dsw-alias-bg-base")) throw new Error("token block missing");
if (sheet.textContent.includes("table tbody tr:nth-child(odd)")) {
    throw new Error("table rules must stay out of the colour stylesheet");
}
if (!table.textContent.includes("border: 1px solid #343943")) {
    throw new Error("default border axis is missing");
}
const oddBlock = /nth-child\(odd\)\s*\{([^}]*)\}/.exec(table.textContent);
const evenBlock = /nth-child\(even\)\s*\{([^}]*)\}/.exec(table.textContent);
if (!oddBlock || !oddBlock[1].includes("transparent")) {
    throw new Error("default stripe must leave the first row clear");
}
if (!evenBlock || !evenBlock[1].includes("#262a31")) {
    throw new Error("default stripe must tint the second row");
}

if (!sectionSpec || sectionSpec.id !== "onedark-palette") {
    throw new Error("palette section did not register");
}
if (sectionSpec.name !== "settings.section") throw new Error("wrong slot for the section");
if (typeof sectionSpec.label !== "function" || sectionSpec.label() !== "配色方案") {
    throw new Error("section label is wrong");
}

const walk = (node, out = []) => {
    if (node === null || node === undefined) return out;
    if (Array.isArray(node)) { node.forEach((n) => walk(n, out)); return out; }
    if (typeof node !== "object") return out;
    out.push(node);
    if (node.props && node.props.children !== undefined) walk(node.props.children, out);
    return out;
};

const tree = sectionComponent();
const nodes = walk(tree);
const selects = nodes.filter((n) => n.type === "select");
if (selects.length !== 2) throw new Error("expected two choosers, got " + selects.length);
if (selects[0].props.value !== "grid") throw new Error("border chooser default is wrong");
if (selects[1].props.value !== "after") throw new Error("stripe chooser default is wrong");
const borderOptions = (selects[0].props.children || []).map((o) => o.props.value);
const stripeOptions = (selects[1].props.children || []).map((o) => o.props.value);
if (borderOptions.join() !== "grid,rows,none") throw new Error("border options: " + borderOptions.join());
if (stripeOptions.join() !== "after,first,none") throw new Error("stripe options: " + stripeOptions.join());
const swatches = nodes.filter((n) => n.type === "span").length;
if (swatches < 12) throw new Error("palette swatches missing, got " + swatches);

// legacy single-mode value must migrate to the two axes
store.set("onedark.tableStyle", "zebra");
exportsObj.apply(ctx);
if (store.get("onedark.tableBorder") !== "none") throw new Error("legacy border did not migrate");
if (store.get("onedark.tableStripe") !== "first") throw new Error("legacy stripe did not migrate");
if (store.has("onedark.tableStyle")) throw new Error("legacy key was not cleared");

console.log("ok: 2 stylesheets, 2 choosers, 12 swatches, legacy mode migrates");
console.log("colour css:", sheet.textContent.length, "| table css:", table.textContent.length);
