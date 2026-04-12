import { existsSync, readFileSync } from "node:fs";
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

  it("documents the new style layers and page shell usage", () => {
    const source = readFileSync(resolve(process.cwd(), "src/styles/README.md"), "utf8");

    expect(source).toContain("tokens -> theme -> foundation -> skins -> pages");
    expect(source).toContain("PageShell");
    expect(source).toContain("FilterPanel");
    expect(source).toContain("DataPanel");
  });

  it("drops dead legacy search and table helpers from the active stylesheet graph", () => {
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(css).not.toContain(".search-container");
    expect(css).not.toContain(".data-table");
    expect(existsSync(resolve(process.cwd(), "src/styles/pages/_system.scss"))).toBe(false);
  });

  it("keeps element-plus custom table overrides free of legacy minimal selectors", () => {
    const tableSkinSource = readFileSync(
      resolve(process.cwd(), "src/styles/element-plus-custom/_table.scss"),
      "utf8"
    );

    expect(tableSkinSource).not.toContain(".minimal-table");
  });
});
