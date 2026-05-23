import { afterEach, describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { compileStyle, injectStyle, resetThemeTestDom } from "./theme-style-test-utils";

describe("theme form and shell chrome", () => {
  afterEach(resetThemeTestDom);

  it("styles shared shell panels and tables through ff semantic hooks", () => {
    const css = compileStyle("src/styles/index.scss");

    injectStyle(css);
    document.body.innerHTML = `
      <section class="ff-page-shell">
        <section class="ff-filter-panel"></section>
        <section class="ff-data-panel">
          <div class="ff-data-panel__body">
            <table class="ff-table"></table>
          </div>
        </section>
      </section>
    `;

    const filterPanel = document.querySelector(".ff-filter-panel") as HTMLElement;
    const dataPanel = document.querySelector(".ff-data-panel") as HTMLElement;

    expect(getComputedStyle(filterPanel).borderRadius).toBe("16px");
    expect(getComputedStyle(dataPanel).backgroundColor).not.toBe("");
  });

  it("keeps field spacing for regular ff forms while collapsing toolbar forms", () => {
    const css = compileStyle("src/styles/index.scss");

    injectStyle(css);
    document.body.innerHTML = `
      <form class="el-form ff-form">
        <div class="el-form-item">
          <label class="el-form-item__label">用户名</label>
        </div>
      </form>
      <form class="el-form ff-form ff-toolbar">
        <div class="el-form-item">
          <label class="el-form-item__label">关键字</label>
        </div>
      </form>
    `;

    const regularItem = document.querySelector(
      ".ff-form:not(.ff-toolbar) .el-form-item"
    ) as HTMLElement;
    const toolbarItem = document.querySelector(".ff-toolbar .el-form-item") as HTMLElement;

    expect(getComputedStyle(regularItem).marginBottom).toBe("20px");
    expect(getComputedStyle(toolbarItem).marginBottom).toBe("0px");
  });

  it("keeps ff drawers readable in dark mode", () => {
    const css = compileStyle("src/styles/index.scss");

    injectStyle(css);
    document.body.innerHTML = `
      <div class="el-drawer ff-drawer">
        <header class="el-drawer__header">
          <span class="el-drawer__title">编辑用户</span>
        </header>
        <div class="el-drawer__body">
          <form class="el-form ff-form">
            <div class="el-form-item">
              <label class="el-form-item__label">用户名</label>
              <div class="el-form-item__content">
                <div class="el-input">
                  <div class="el-input__wrapper">
                    <input class="el-input__inner" value="admin" />
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const drawer = document.querySelector(".ff-drawer") as HTMLElement;
    const label = document.querySelector(".el-form-item__label") as HTMLElement;
    const input = document.querySelector(".el-input__inner") as HTMLInputElement;

    expect(getComputedStyle(drawer).backgroundColor).toBe("#1e293b");
    expect(getComputedStyle(label).color).toBe("#cbd5e1");
    expect(getComputedStyle(input).color).toBe("#f1f5f9");
    expect(getComputedStyle(input).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });

  it("lets ff dialogs and drawers inherit the global light-mode chrome", () => {
    const css = compileStyle("src/styles/index.scss");
    const dialogSkin = readFileSync(
      resolve(process.cwd(), "src/styles/skins/_dialog.scss"),
      "utf8"
    );
    const drawerSkin = readFileSync(
      resolve(process.cwd(), "src/styles/skins/_drawer.scss"),
      "utf8"
    );
    const dialogLightSkin = dialogSkin.split("html.dark")[0];
    const drawerLightSkin = drawerSkin.split("html.dark")[0];

    expect(css).toContain(
      "background: linear-gradient(135deg, var(--gray-50, #f9fafb) 0%, #ffffff 100%);"
    );
    expect(dialogLightSkin).not.toMatch(
      /\.ff-dialog[\s\S]*?\.el-dialog__header[\s\S]*?\{[^}]*background:/
    );
    expect(dialogLightSkin).not.toMatch(
      /\.ff-dialog[\s\S]*?\.el-dialog__footer[\s\S]*?\{[^}]*background:/
    );
    expect(drawerLightSkin).not.toMatch(
      /\.ff-drawer[\s\S]*?\.el-drawer__header[\s\S]*?\{[^}]*background:/
    );
    expect(drawerLightSkin).not.toMatch(
      /\.ff-drawer[\s\S]*?\.el-drawer__footer[\s\S]*?\{[^}]*background:/
    );
  });
});
