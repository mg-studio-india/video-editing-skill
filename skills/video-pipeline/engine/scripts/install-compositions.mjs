#!/usr/bin/env node
/**
 * install-compositions.mjs: install all HyperFrames compositions and components into the engine library.
 */
import { execFile } from "child_process";
import fs from "fs";
import path from "path";
import os from "os";

const args = process.argv.slice(2);
let targetDir = process.env.VIDEO_ENGINE_DIR || path.join(os.homedir(), ".video-skills", "engine");
let concurrency = 12;
let force = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--target" && args[i + 1]) targetDir = args[++i];
  else if (args[i] === "--concurrency" && args[i + 1]) concurrency = parseInt(args[++i], 10) || 12;
  else if (args[i] === "--force") force = true;
  else if (args[i] === "-h" || args[i] === "--help") {
    console.log("Usage: node install-compositions.mjs [--target <dir>] [--concurrency <n>] [--force]");
    process.exit(0);
  }
}

targetDir = path.resolve(targetDir);
const compositionsDir = path.join(targetDir, "compositions");
const componentsDir = path.join(compositionsDir, "components");
fs.mkdirSync(componentsDir, { recursive: true });

// Locate HyperFrames CLI binary
let hfBin = null;
const candidateBins = [
  path.join(targetDir, "node_modules", "hyperframes", "bin", "hyperframes.mjs"),
  path.join(os.homedir(), ".video-skills", "engine", "node_modules", "hyperframes", "bin", "hyperframes.mjs"),
  path.join(process.cwd(), "node_modules", "hyperframes", "bin", "hyperframes.mjs")
];
for (const b of candidateBins) {
  if (fs.existsSync(b)) {
    hfBin = b;
    break;
  }
}

// Locate catalog items from cache or via CLI
let catalogItems = [];
const cachePath = "/tmp/hyperframes-catalog.json";
if (fs.existsSync(cachePath)) {
  try {
    catalogItems = JSON.parse(fs.readFileSync(cachePath, "utf8"));
  } catch (e) {}
}

async function getCatalog() {
  if (catalogItems.length > 0) return catalogItems;
  return new Promise((resolve) => {
    const bin = hfBin || "hyperframes";
    const proc = execFile("node", [bin, "catalog", "--json"], { maxBuffer: 50 * 1024 * 1024 }, (err, stdout) => {
      if (!err && stdout) {
        try {
          const data = JSON.parse(stdout);
          resolve(data.results || data);
          return;
        } catch (e) {}
      }
      resolve([]);
    });
  });
}

async function main() {
  console.log(`[HyperFrames Compositions Installer] Target library: ${compositionsDir}`);
  const items = await getCatalog();
  if (!items || items.length === 0) {
    console.error("[HyperFrames Compositions Installer] Error: Unable to load catalog items.");
    process.exit(1);
  }

  console.log(`[HyperFrames Compositions Installer] Discovered ${items.length} compositions & components in catalog.`);

  let installed = 0;
  let skipped = 0;
  let failed = 0;
  const total = items.length;
  let idx = 0;

  async function worker() {
    while (idx < items.length) {
      const current = items[idx++];
      const name = current.name;
      const isComp = current.type === "component";
      const destPath = isComp
        ? path.join(componentsDir, `${name}.html`)
        : path.join(compositionsDir, `${name}.html`);

      if (!force && fs.existsSync(destPath)) {
        skipped++;
        continue;
      }

      await new Promise((resolve) => {
        const bin = hfBin || "hyperframes";
        execFile("node", [bin, "add", name, "--dir", targetDir, "--no-clipboard"], (err) => {
          if (err) {
            failed++;
          } else {
            installed++;
          }
          resolve();
        });
      });
    }
  }

  const workers = [];
  for (let w = 0; w < Math.min(concurrency, total); w++) {
    workers.push(worker());
  }

  const progressInterval = setInterval(() => {
    const done = installed + skipped + failed;
    const pct = Math.round((done / total) * 100);
    process.stdout.write(`\r[HyperFrames Compositions Installer] Progress: ${done}/${total} (${pct}%) · ${installed} added, ${skipped} existing, ${failed} failed`);
  }, 1000);

  await Promise.all(workers);
  clearInterval(progressInterval);
  process.stdout.write("\n");

  console.log(`[HyperFrames Compositions Installer] Complete: ${installed} added, ${skipped} already cached, ${failed} failed.`);
  console.log(`[HyperFrames Compositions Installer] Library verified at: ${compositionsDir}`);
}

main().catch((err) => {
  console.error("[HyperFrames Compositions Installer] Fatal error:", err);
  process.exit(1);
});
