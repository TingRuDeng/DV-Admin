import { existsSync, readdirSync, readFileSync } from "node:fs";
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

  it("keeps layout chrome selectors out of the compatibility shim", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).not.toContain(".navbar,\n.layout-header");
    expect(source).not.toContain(".sidebar-logo-link");
    expect(source).not.toContain(".layout__sidebar");
    expect(source).not.toContain(".navbar-actions__item");
    expect(source).not.toContain(".user-profile__avatar");
  });

  it("moves active dialog, tag, and panel aliases out of the compatibility shim", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).not.toContain(".minimal-dialog");
    expect(source).not.toContain(".minimal-tag");
    expect(source).not.toContain(".minimal-search-container");
    expect(source).not.toContain(".minimal-data-container");
  });

  it("keeps legacy form, pagination, and glass aliases out of the compatibility shim", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).not.toContain(".minimal-form");
    expect(source).not.toContain(".minimal-pagination");
    expect(source).not.toContain(".glass-panel");
  });

  it("moves minimal button, input, and table aliases into the skin layer", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).not.toContain(".minimal-btn");
    expect(source).not.toContain(".minimal-input");
    expect(source).not.toContain(".minimal-table");
  });

  it("moves active menu and tree skins out of the compatibility shim", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).not.toContain(".transparent-tree");
    expect(source).not.toContain(".el-menu {\n");
    expect(source).not.toContain(".el-menu-item,\n.el-sub-menu__title");
    expect(source).not.toContain(".el-menu-item:hover i");
  });

  it("keeps component-level dark fallbacks out of the compatibility shim", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/_minimal-saas.scss"), "utf8");

    expect(source).not.toContain(".el-select__wrapper");
    expect(source).not.toContain(".el-radio__label");
    expect(source).not.toContain(".el-input__wrapper");
    expect(source).not.toContain(".el-pagination button");
    expect(source).not.toContain(".el-popper.is-light");
    expect(source).not.toContain(".el-dropdown-menu__item");
  });

  it("documents the new style layers and page shell usage", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/README.md"), "utf8");

    expect(source).toContain("tokens -> theme -> foundation -> skins -> pages");
    expect(source).toContain("PageShell");
    expect(source).toContain("FilterPanel");
    expect(source).toContain("DataPanel");
  });

  it("freezes the compatibility shim behind an explicit legacy whitelist", () => {
    const shimSource = readFileSync(
      resolve(process.cwd(), "src/styles/_minimal-saas.scss"),
      "utf8"
    );
    const readmeSource = readFileSync(resolve(process.cwd(), "src/styles/README.md"), "utf8");

    expect(shimSource).toContain("Legacy shim whitelist");
    expect(readmeSource).toContain("frozen legacy shim");
    expect(readmeSource).toContain("text-fill fallback");
    expect(readmeSource).toContain("brand gradient preservation");
    expect(readmeSource).toContain("utility-class dark fallbacks");
  });

  it("drops dead legacy search and table helpers from the active stylesheet graph", () => {
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(css).not.toContain(".search-container");
    expect(css).not.toContain(".data-table");
    expect(existsSync(resolve(process.cwd(), "src/styles/pages/_system.scss"))).toBe(false);
  });

  it("keeps legacy minimal and glass aliases out of the active stylesheet graph", () => {
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(css).not.toContain(".minimal-btn");
    expect(css).not.toContain(".minimal-form");
    expect(css).not.toContain(".minimal-input");
    expect(css).not.toContain(".minimal-table");
    expect(css).not.toContain(".minimal-dialog");
    expect(css).not.toContain(".minimal-tag");
    expect(css).not.toContain(".minimal-search-container");
    expect(css).not.toContain(".minimal-data-container");
    expect(css).not.toContain(".minimal-pagination");
    expect(css).not.toContain(".glass-panel");
  });

  it("keeps element-plus custom table overrides free of legacy minimal selectors", () => {
    const tableSkinSource = readFileSync(
      resolve(process.cwd(), "src/styles/element-plus-custom/_table.scss"),
      "utf8"
    );

    expect(tableSkinSource).not.toContain(".minimal-table");
  });
});

describe("liquid chrome visual system governance", () => {
  const sourceFiles = () =>
    (readdirSync(resolve(process.cwd(), "src"), { recursive: true }) as string[])
      .filter((file) => /\.(vue|ts|scss|css)$/.test(file) && !file.includes("__tests__"))
      .map((file) => ({ file, source: readFileSync(resolve(process.cwd(), "src", file), "utf8") }));

  it("exposes iridescent and glass tokens from the entry stylesheet", () => {
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(css).toContain("--ff-iri-a");
    expect(css).toContain("--ff-iri:");
    expect(css).toContain("--ff-on-iri");
    expect(css).toContain("--ff-glass-fx");
    expect(css).toMatch(/@font-face\s*\{\s*font-family: "?Geist"?;/);
  });

  it("self-hosts the Geist fonts together with their license", () => {
    for (const asset of [
      "geist-latin-wght-normal.woff2",
      "geist-mono-latin-wght-normal.woff2",
      "OFL.txt",
    ]) {
      expect(existsSync(resolve(process.cwd(), "src/assets/fonts", asset)), asset).toBe(true);
    }
  });

  it("keeps custom cursors and WebGL canvases out of the app", () => {
    for (const { file, source } of sourceFiles()) {
      expect(source, file).not.toMatch(/cursor:\s*url\(/);
      expect(source, file).not.toMatch(/getContext\(\s*["']webgl/);
    }
  });

  it("confines backdrop-filter to the glass mixin and the popper skin", () => {
    const allowed = new Set(["styles/foundation/_glass.scss", "styles/skins/_popper.scss"]);
    const offenders = sourceFiles()
      .filter(({ source }) => /backdrop-filter\s*:/.test(source))
      .map(({ file }) => file.split("\\").join("/"))
      .filter((file) => !allowed.has(file));

    expect(offenders).toEqual([]);
  });

  it("keeps legacy element-plus overrides free of indigo literals and hover lifts", () => {
    const legacyFiles = [
      "src/styles/element-plus.scss",
      ...readdirSync(resolve(process.cwd(), "src/styles/element-plus-custom")).map(
        (file) => `src/styles/element-plus-custom/${file}`
      ),
    ];

    for (const file of legacyFiles) {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");

      expect(source, file).not.toMatch(/#6366f1|#4f46e5|#818cf8|99,\s*102,\s*241/i);
      expect(source, file).not.toContain("translateY(-");
    }
  });
});
