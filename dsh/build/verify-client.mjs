// Load the built client bundle against a stubbed DOM and check that applying
// the plugin inserts exactly one stylesheet carrying the override rules.
import fs from "node:fs";
import path from "node:path";

const here = import.meta.dirname;
const file = path.join(path.dirname(here), "plugin", "lib", "client.js");
const source = fs.readFileSync(file, "utf-8");

const created = [];
const styleTags = [];

const document = {
    head: {
        appendChild(node) {
            created.push(node);
            styleTags.push(node);
            return node;
        },
    },
    createElement(tag) {
        return { tag, dataset: {}, textContent: "" };
    },
    querySelector(selector) {
        const wanted = /data-plugin-css="([^"]+)"/.exec(selector);
        if (!wanted) return null;
        return styleTags.find((tag) => tag.dataset.pluginCss === wanted[1]) || null;
    },
};

let registered = null;
const window = {
    __ModuleLoader__: {
        load(entry) {
            registered = entry;
        },
    },
};

const run = new Function("window", "document", source);
run(window, document);

if (!registered) throw new Error("plugin did not register with the module loader");
if (registered.id !== "dsh-onedark") throw new Error("unexpected plugin id: " + registered.id);

const exportsObj = registered.factory(() => {
    throw new Error("the plugin must not require any client module");
});
if (typeof exportsObj.apply !== "function") throw new Error("missing apply export");

exportsObj.apply({});
if (created.length !== 1) throw new Error("expected one stylesheet, got " + created.length);

const tag = created[0];
if (tag.tag !== "style") throw new Error("expected a style element");
if (tag.dataset.plugin !== "dsh-onedark") throw new Error("plugin dataset mismatch");
if (!tag.textContent.includes("_3GBCTG_thinkBody")) throw new Error("stylesheet lost the reasoning rule");
if (!tag.textContent.includes("border-left")) throw new Error("stylesheet lost the rule line");

// second apply must not stack a duplicate sheet
exportsObj.apply({});
if (created.length !== 1) throw new Error("plugin injected a duplicate stylesheet");

console.log("ok: plugin registers, applies once, injects", tag.textContent.length, "bytes of CSS");
console.log("inject deps:", JSON.stringify(exportsObj.inject));
