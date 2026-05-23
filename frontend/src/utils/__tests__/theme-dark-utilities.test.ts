import { afterEach, describe, expect, it } from "vitest";
import { compileStyle, injectStyle, resetThemeTestDom } from "./theme-style-test-utils";

describe("dark theme utility overrides", () => {
  afterEach(resetThemeTestDom);

  it("keeps glass table surfaces and slate utility text readable in dark mode", () => {
    const resetCss = compileStyle("src/styles/reset.scss");
    const minimalSaasCss = compileStyle("src/styles/_minimal-saas.scss");

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

  it("keeps slate utility badges readable inside ff page shells in dark mode", () => {
    const resetCss = compileStyle("src/styles/reset.scss");
    const minimalSaasCss = compileStyle("src/styles/_minimal-saas.scss");

    injectStyle(`
      :root {
        --el-text-color-primary: rgb(30, 41, 59);
        --el-text-color-secondary: rgb(148, 163, 184);
      }

      html.dark {
        --el-text-color-primary: rgb(241, 245, 249);
        --el-text-color-secondary: rgb(203, 213, 225);
      }
    `);
    injectStyle(resetCss);
    injectStyle(minimalSaasCss);

    document.body.innerHTML = `
      <section class="ff-page-shell">
        <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">10</span>
      </section>
    `;
    document.documentElement.classList.add("dark");

    const badge = document.querySelector(".text-slate-400") as HTMLSpanElement;

    expect(getComputedStyle(badge).color).toBe("rgb(203, 213, 225)");
    expect(getComputedStyle(badge).backgroundColor).toBe("rgba(255, 255, 255, 0.08)");
  });

  it("forces webkit text fill to follow current text color inside dark layout containers", () => {
    const resetCss = compileStyle("src/styles/reset.scss");
    const minimalSaasCss = compileStyle("src/styles/_minimal-saas.scss");

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
});
