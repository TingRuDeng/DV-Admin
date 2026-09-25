import { afterEach, describe, expect, it } from "vitest";
import { compileStyle, injectStyle, resetThemeTestDom } from "./theme-style-test-utils";

describe("dark theme overlay popups", () => {
  afterEach(resetThemeTestDom);

  it("keeps teleported dropdown items readable in dark mode", () => {
    const tokensCss = compileStyle("src/styles/tokens/index.scss");
    const resetCss = compileStyle("src/styles/reset.scss");
    const darkThemeCss = compileStyle("src/styles/theme/_dark.scss");

    injectStyle(tokensCss);
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

    expect(getComputedStyle(popper).backgroundColor).toBe("rgba(16, 16, 22, 0.92)");
    expect(getComputedStyle(item).color).toBe("#d6d6dc");
    expect(getComputedStyle(item).getPropertyValue("-webkit-text-fill-color")).toBe("currentColor");
    expect(getComputedStyle(dividedItem).borderTopColor).toBe("rgba(255, 255, 255, 0.08)");
  });

  it("keeps the teleported navbar menu search panel opaque in dark mode", () => {
    const tokensCss = compileStyle("src/styles/tokens/index.scss");
    const resetCss = compileStyle("src/styles/reset.scss");
    const darkThemeCss = compileStyle("src/styles/theme/_dark.scss");

    injectStyle(tokensCss);
    injectStyle(resetCss);
    injectStyle(darkThemeCss);

    document.body.innerHTML = `
      <div class="menu-search__panel">
        <ul role="listbox" class="menu-search__listbox">
          <li role="option" class="menu-search__option">角色管理</li>
        </ul>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const panel = document.querySelector(".menu-search__panel") as HTMLDivElement;

    expect(getComputedStyle(panel).backgroundColor).toBe("rgba(16, 16, 22, 0.92)");
    expect(getComputedStyle(panel).color).toBe("#d6d6dc");
    expect(getComputedStyle(panel).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });

  it("gives the navbar menu search panel the shared popper glass skin", () => {
    const popperSkin = compileStyle("src/styles/skins/_popper.scss");

    expect(popperSkin).toMatch(
      /html \.menu-search__panel\s*\{[^}]*background: var\(--ff-popper-bg\);[^}]*backdrop-filter: var\(--ff-glass-fx\);/
    );
  });

  it("keeps message box prompts readable in dark mode", () => {
    const css = compileStyle("src/styles/index.scss");

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
    expect(getComputedStyle(input).color).toBe("#f4f4f6");
    expect(getComputedStyle(input).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });

  it("keeps info messages readable in dark mode", () => {
    const css = compileStyle("src/styles/index.scss");

    injectStyle(css);
    document.body.innerHTML = `
      <div class="el-message el-message--info">
        <p class="el-message__content">已取消删除</p>
      </div>
    `;
    document.documentElement.classList.add("dark");

    const message = document.querySelector(".el-message") as HTMLElement;
    const content = document.querySelector(".el-message__content") as HTMLElement;

    expect(getComputedStyle(message).backgroundColor).toBe("rgba(16, 16, 22, 0.92)");
    expect(getComputedStyle(content).color).toBe("#d6d6dc");
    expect(getComputedStyle(content).getPropertyValue("-webkit-text-fill-color")).toBe(
      "currentColor"
    );
  });
});
