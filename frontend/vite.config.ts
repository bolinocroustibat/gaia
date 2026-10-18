import { execSync } from "node:child_process";
import { cpSync, createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig, type Plugin } from "vite";

const root = path.dirname(fileURLToPath(import.meta.url));
const processedSource = path.resolve(root, "../data/processed");
const pkg = JSON.parse(readFileSync(new URL("./package.json", import.meta.url), "utf8")) as {
  version: string;
};
const commit = execSync("git rev-parse --short=8 HEAD", { encoding: "utf8" }).trim();

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
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
    __APP_COMMIT__: JSON.stringify(commit),
  },
  plugins: [svelte(), processedData()],
});
