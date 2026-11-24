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

const primitives = {
    Menu: function Menu(props) {
        return { type: Menu, props };
    },
    IconChevronDownOutlineRegular: function Chevron(props) {
        return { type: "svg", props: { ...props, children: [] } };
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
    if (name === "@deepseek-ai/dsh-client-ui-primitives") return primitives;
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
if (!table.textContent.includes("white-space: normal")) {
    throw new Error("default flow must fold long cells");
}
if (table.textContent.includes("white-space: nowrap")) {
    throw new Error("default flow must not scroll");
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
const menus = nodes.filter((n) => n.type === primitives.Menu);
if (menus.length !== 3) throw new Error("expected three app menus, got " + menus.length);
if (menus[0].props.selectedId !== "grid") throw new Error("border chooser default is wrong");
if (menus[1].props.selectedId !== "after") throw new Error("stripe chooser default is wrong");
if (menus[2].props.selectedId !== "wrap") throw new Error("flow chooser default is wrong");
const borderIds = menus[0].props.items.map((i) => i.id).join();
const stripeIds = menus[1].props.items.map((i) => i.id).join();
if (borderIds !== "grid,rows,none") throw new Error("border options: " + borderIds);
if (stripeIds !== "after,first,none") throw new Error("stripe options: " + stripeIds);
const triggers = menus.map((m) => m.props.anchor);
if (triggers.some((t2) => !t2 || t2.type !== "button")) {
    throw new Error("each menu needs a button anchor");
}
if (triggers[0].props.className !== "dsh-od-chooser") throw new Error("anchor class is wrong");
const flowIds = menus[2].props.items.map((i) => i.id).join();
if (flowIds !== "wrap,scroll") throw new Error("flow options: " + flowIds);
if (triggers[0].props["aria-haspopup"] !== "menu") throw new Error("trigger is not a menu trigger");
const swatches = nodes.filter((n) => n.type === "span").length;
if (swatches < 12) throw new Error("palette swatches missing, got " + swatches);

// legacy single-mode value must migrate to the two axes
store.set("onedark.tableStyle", "zebra");
exportsObj.apply(ctx);
if (store.get("onedark.tableBorder") !== "none") throw new Error("legacy border did not migrate");
if (store.get("onedark.tableStripe") !== "first") throw new Error("legacy stripe did not migrate");
if (store.get("onedark.tableFlow") !== "wrap") throw new Error("legacy flow did not migrate");
if (store.has("onedark.tableStyle")) throw new Error("legacy key was not cleared");

console.log("ok: 2 stylesheets, 2 choosers, 12 swatches, legacy mode migrates");
console.log("colour css:", sheet.textContent.length, "| table css:", table.textContent.length);
