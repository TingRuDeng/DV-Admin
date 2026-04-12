import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { compile } from "sass";
import { describe, expect, it } from "vitest";

describe("style governance entrypoint", () => {
  it("compiles layered styles and exposes the shared page-shell hooks", () => {
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(css).toContain(".ff-page-shell");
    expect(css).toContain("--ff-color-bg-page");
    expect(css).toContain("linear-gradient(135deg");
  });

  it("keeps _minimal-saas.scss as a compatibility shim instead of the primary rule dump", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).toContain("Temporary compatibility layer");
    expect(source).not.toContain(".minimal-btn {");
  });

  it("documents the new style layers and page shell usage", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/README.md"), "utf8");

    expect(source).toContain("tokens -> theme -> foundation -> skins -> pages");
    expect(source).toContain("PageShell");
    expect(source).toContain("FilterPanel");
    expect(source).toContain("DataPanel");
  });
});
