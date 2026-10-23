// Resolve a Chromium browser executable without hard coding a local install path.
// The verification scripts drive the browser over CDP, so any Chromium based
// browser works. Set EDGE_PATH to override the lookup.

import { execFileSync } from "node:child_process";

const CANDIDATES = ["msedge", "chrome", "chromium", "chromium-browser"];

function fromPath(name) {
    const finder = process.platform === "win32" ? "where" : "which";
    try {
        const out = execFileSync(finder, [name], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
        const hit = out.split(/\r?\n/).map((line) => line.trim()).find(Boolean);
        return hit || null;
    } catch {
        return null;
    }
}

function resolveBrowser() {
    if (process.env.EDGE_PATH) return process.env.EDGE_PATH;
    for (const name of CANDIDATES) {
        const hit = fromPath(name);
        if (hit) return hit;
    }
    throw new Error("no Chromium browser found; set EDGE_PATH to the executable");
}

export const BROWSER = resolveBrowser();
