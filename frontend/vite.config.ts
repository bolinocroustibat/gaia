import { cpSync, createReadStream, existsSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig, type Plugin } from "vite";

const root = path.dirname(fileURLToPath(import.meta.url));
const processedSource = path.resolve(root, "../data/processed");

function processedData(): Plugin {
  let outDir = path.resolve(root, "dist");

  return {
    name: "gaia-processed-data",
    configResolved(config) {
      outDir = path.resolve(config.root, config.build.outDir);
    },
    configureServer(server) {
      server.middlewares.use("/processed", (req, res, next) => {
        let relativePath = "";
        try {
          relativePath = decodeURIComponent((req.url ?? "/").split("?")[0] ?? "/").replace(
            /^\/+/,
            "",
          );
        } catch {
          next();
          return;
        }
        if (relativePath.includes("\0")) {
          next();
          return;
        }
        const file = path.resolve(processedSource, relativePath);
        const relative = path.relative(processedSource, file);
        if (relative.startsWith("..") || path.isAbsolute(relative)) {
          next();
          return;
        }
        if (!existsSync(file) || !statSync(file).isFile()) {
          next();
          return;
        }
        res.setHeader("Content-Type", "application/json; charset=utf-8");
        res.setHeader("Cache-Control", "no-cache");
        createReadStream(file).pipe(res);
      });
    },
    closeBundle() {
      cpSync(processedSource, path.join(outDir, "processed"), { recursive: true });
    },
  };
}

export default defineConfig({
  plugins: [svelte(), processedData()],
});
