import { afterEach, describe, expect, it, vi } from "vitest";
import { applyTheme, generateThemeColors } from "@/utils/theme";
import { ThemeMode } from "@/enums";

const originalRequestAnimationFrame = globalThis.requestAnimationFrame;

afterEach(() => {
  document.documentElement.removeAttribute("style");
  globalThis.requestAnimationFrame = originalRequestAnimationFrame;
});

describe("applyTheme", () => {
  it.each([
    ["#ff705c", "#000000"],
    ["#123456", "#ffffff"],
    ["#ffffff", "#000000"],
    ["#000000", "#ffffff"],
  ])("keeps filled action text readable for %s", (primary, foreground) => {
    globalThis.requestAnimationFrame = vi.fn() as typeof requestAnimationFrame;
    applyTheme({ primary });
    expect(document.documentElement.style.getPropertyValue("--ff-accent-text")).toBe(foreground);
  });

  it("keeps custom design tokens in sync with Element Plus tokens", () => {
    globalThis.requestAnimationFrame = vi.fn() as typeof requestAnimationFrame;

    applyTheme({
      primary: "#123456",
      "primary-light-3": "#abcdef",
    });

    expect(document.documentElement.style.getPropertyValue("--el-color-primary")).toBe("#123456");
    expect(document.documentElement.style.getPropertyValue("--color-primary")).toBe("#123456");
    expect(document.documentElement.style.getPropertyValue("--ff-accent")).toBe("#123456");
    expect(document.documentElement.style.getPropertyValue("--ff-accent-strong")).toBe("#132e49");
  });

  it("uses the generated darker token for strong accent states", () => {
    globalThis.requestAnimationFrame = vi.fn() as typeof requestAnimationFrame;

    applyTheme({
      primary: "#ff705c",
      "primary-dark-2": "#d05e4e",
    });

    expect(document.documentElement.style.getPropertyValue("--ff-accent-strong")).toBe("#d05e4e");
  });

  it("keeps primary-dark-2 darker in light mode", () => {
    const colors = generateThemeColors("#ff705c", ThemeMode.LIGHT);

    expect(colors["primary-dark-2"]).toBe("#d05e4e");
  });
});
