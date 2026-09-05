import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: "happy-dom",
    // Node 24 的实验性 Web Storage 会抢占 happy-dom 注入的 localStorage。
    execArgv: ["--no-experimental-webstorage"],
    setupFiles: ["./vitest.setup.ts"],
    include: ["src/**/*.{test,spec}.{js,ts}"],
    exclude: ["node_modules", "dist", "e2e"],
    pool: "forks",
    fileParallelism: false,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "dist/",
        "e2e/",
        "**/*.d.ts",
        "**/*.config.{js,ts}",
        "src/main.ts",
        "src/App.vue",
      ],
    },
  },
  resolve: {
    alias: {
      "@": resolve(import.meta.dirname, "src"),
    },
  },
});
