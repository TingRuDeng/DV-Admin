import { afterEach, describe, expect, it } from "vitest";
import { compile } from "sass";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function injectStyle(cssText: string) {
  const style = document.createElement("style");
  style.textContent = cssText;
  document.head.appendChild(style);
}

describe("dark theme utility overrides", () => {
  afterEach(() => {
    document.head.innerHTML = "";
    document.body.innerHTML = "";
    document.documentElement.className = "";
  });

  it("keeps glass table surfaces and slate utility text readable in dark mode", () => {
    const resetScssPath = resolve(process.cwd(), "src/styles/reset.scss");
    const minimalSaasScssPath = resolve(process.cwd(), "src/styles/_minimal-saas.scss");
    const resetCss = compile(resetScssPath).css;
    const minimalSaasCss = compile(minimalSaasScssPath).css;

    injectStyle(`
      :root {
        --el-bg-color-page: rgb(245, 248, 253);
        --el-bg-color-overlay: rgb(255, 255, 255);
        --el-text-color-primary: rgb(30, 41, 59);
        --el-text-color-regular: rgb(71, 85, 105);
        --el-text-color-secondary: rgb(148, 163, 184);
        --el-border-color: rgb(203, 213, 225);
      }

      html.dark {
        --el-bg-color-page: rgb(15, 23, 42);
        --el-bg-color-overlay: rgb(30, 41, 59);
        --el-text-color-primary: rgb(241, 245, 249);
        --el-text-color-regular: rgb(226, 232, 240);
        --el-text-color-secondary: rgb(203, 213, 225);
        --el-border-color: rgba(255, 255, 255, 0.1);
      }
    `);
    injectStyle(resetCss);
    injectStyle(minimalSaasCss);

    document.body.innerHTML = `
      <div class="app-container">
        <div class="bg-white/20 border-slate-100/50">
          <span class="text-slate-700">标题</span>
          <span class="text-slate-400 bg-slate-50">编号</span>
        </div>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const surface = document.querySelector(".bg-white\\/20");
    const title = document.querySelector(".text-slate-700");
    const meta = document.querySelector(".text-slate-400");

    expect(getComputedStyle(surface as HTMLDivElement).backgroundColor).toBe(
      "rgba(15, 23, 42, 0.28)"
    );
    expect(getComputedStyle(title as HTMLSpanElement).color).toBe("rgb(241, 245, 249)");
    expect(getComputedStyle(meta as HTMLSpanElement).color).toBe("rgb(203, 213, 225)");
    expect(getComputedStyle(meta as HTMLSpanElement).backgroundColor).toBe(
      "rgba(255, 255, 255, 0.08)"
    );
  });

  it("forces webkit text fill to follow current text color inside dark layout containers", () => {
    const resetScssPath = resolve(process.cwd(), "src/styles/reset.scss");
    const minimalSaasScssPath = resolve(process.cwd(), "src/styles/_minimal-saas.scss");
    const resetCss = compile(resetScssPath).css;
    const minimalSaasCss = compile(minimalSaasScssPath).css;

    injectStyle(`
      :root {
        --el-text-color-primary: rgb(30, 41, 59);
      }

      html.dark {
        --el-text-color-primary: rgb(241, 245, 249);
      }
    `);
    injectStyle(resetCss);
    injectStyle(minimalSaasCss);

    document.body.innerHTML = `
      <div class="layout-wrapper">
        <div class="app-container">
          <span class="text-slate-700">用户数据</span>
        </div>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const contentText = document.querySelector(".text-slate-700") as HTMLSpanElement;

    expect(getComputedStyle(contentText).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });

  it("keeps teleported dropdown items readable in dark mode", () => {
    const resetScssPath = resolve(process.cwd(), "src/styles/reset.scss");
    const darkThemeScssPath = resolve(process.cwd(), "src/styles/theme/_dark.scss");
    const resetCss = compile(resetScssPath).css;
    const darkThemeCss = compile(darkThemeScssPath).css;

    injectStyle(resetCss);
    injectStyle(darkThemeCss);

    document.body.innerHTML = `
      <div class="el-popper is-light el-dropdown__popper">
        <ul class="el-dropdown-menu">
          <li class="el-dropdown-menu__item">个人中心</li>
          <li class="el-dropdown-menu__item el-dropdown-menu__item--divided">退出登录</li>
        </ul>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const popper = document.querySelector(".el-popper") as HTMLDivElement;
    const item = document.querySelector(".el-dropdown-menu__item") as HTMLLIElement;
    const dividedItem = document.querySelector(".el-dropdown-menu__item--divided") as HTMLLIElement;

    expect(getComputedStyle(popper).backgroundColor).toBe("rgba(15, 23, 42, 0.96)");
    expect(getComputedStyle(item).color).toBe("#e2e8f0");
    expect(getComputedStyle(item).getPropertyValue("-webkit-text-fill-color")).toBe("currentColor");
    expect(getComputedStyle(dividedItem).borderTopColor).toBe("rgba(255, 255, 255, 0.08)");
  });

  it("styles shared shell panels and tables through ff semantic hooks", () => {
    const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
    const css = compile(indexScssPath).css;

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
    const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
    const css = compile(indexScssPath).css;

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
    const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
    const css = compile(indexScssPath).css;

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

  it("keeps message box prompts readable in dark mode", () => {
    const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
    const css = compile(indexScssPath).css;

    injectStyle(css);
    document.body.innerHTML = `
      <div class="el-message-box">
        <div class="el-message-box__header">
          <div class="el-message-box__title">重置密码</div>
        </div>
        <div class="el-message-box__content">
          <div class="el-message-box__message">请输入用户【admin】的新密码</div>
          <div class="el-message-box__input">
            <div class="el-input">
              <div class="el-input__wrapper">
                <input class="el-input__inner" value="123456" />
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const box = document.querySelector(".el-message-box") as HTMLElement;
    const title = document.querySelector(".el-message-box__title") as HTMLElement;
    const message = document.querySelector(".el-message-box__message") as HTMLElement;
    const input = document.querySelector(".el-input__inner") as HTMLInputElement;

    expect(getComputedStyle(box).backgroundColor).not.toBe("");
    expect(getComputedStyle(title).color).not.toBe("");
    expect(getComputedStyle(message).color).not.toBe("");
    expect(getComputedStyle(input).color).toBe("#f1f5f9");
    expect(getComputedStyle(input).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });

  it("keeps info messages readable in dark mode", () => {
    const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
    const css = compile(indexScssPath).css;

    injectStyle(css);
    document.body.innerHTML = `
      <div class="el-message el-message--info">
        <p class="el-message__content">已取消删除</p>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const message = document.querySelector(".el-message") as HTMLElement;
    const content = document.querySelector(".el-message__content") as HTMLElement;

    expect(getComputedStyle(message).backgroundColor).toBe("rgba(15, 23, 42, 0.96)");
    expect(getComputedStyle(content).color).toBe("#e2e8f0");
    expect(getComputedStyle(content).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });

  it("lets ff dialogs and drawers inherit the global light-mode chrome", () => {
    const indexScssPath = resolve(process.cwd(), "src/styles/index.scss");
    const dialogSkinPath = resolve(process.cwd(), "src/styles/skins/_dialog.scss");
    const drawerSkinPath = resolve(process.cwd(), "src/styles/skins/_drawer.scss");
    const css = compile(indexScssPath).css;
    const dialogSkin = readFileSync(dialogSkinPath, "utf8");
    const drawerSkin = readFileSync(drawerSkinPath, "utf8");
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
