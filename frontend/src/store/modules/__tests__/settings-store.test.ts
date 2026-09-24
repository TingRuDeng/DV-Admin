import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { STORAGE_KEYS } from "@/constants";
import { defaultSettings } from "@/settings";
import { useSettingsStore } from "@/store/modules/settings-store";

const LEGACY_DEFAULT_THEME_COLOR = "#FF705C";

describe("useSettingsStore 主题色迁移", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    document.documentElement.removeAttribute("style");
  });

  it("新用户直接使用 Liquid Chrome 默认色", () => {
    const store = useSettingsStore();

    expect(store.themeColor).toBe(defaultSettings.themeColor);
    expect(defaultSettings.themeColor).toBe("#6E36D6");
  });

  it("本地存储里的旧默认珊瑚色迁移为新默认色，不区分大小写", async () => {
    localStorage.setItem(STORAGE_KEYS.THEME_COLOR, LEGACY_DEFAULT_THEME_COLOR.toLowerCase());

    const store = useSettingsStore();
    // useStorage 在下一个 tick 才把新值写回本地存储
    await nextTick();

    expect(store.themeColor).toBe(defaultSettings.themeColor);
    expect(localStorage.getItem(STORAGE_KEYS.THEME_COLOR)).toBe(defaultSettings.themeColor);
    expect(localStorage.getItem(STORAGE_KEYS.THEME_COLOR_MIGRATION)).toBe("liquid-chrome");
  });

  it("用户自选的其他颜色保持不动", () => {
    localStorage.setItem(STORAGE_KEYS.THEME_COLOR, "#13C2C2");

    const store = useSettingsStore();

    expect(store.themeColor).toBe("#13C2C2");
  });

  it("迁移只做一次，之后主动选回珊瑚色会被保留", async () => {
    localStorage.setItem(STORAGE_KEYS.THEME_COLOR, LEGACY_DEFAULT_THEME_COLOR);
    useSettingsStore().updateThemeColor(LEGACY_DEFAULT_THEME_COLOR);
    await nextTick();

    setActivePinia(createPinia());
    const reloaded = useSettingsStore();

    expect(reloaded.themeColor).toBe(LEGACY_DEFAULT_THEME_COLOR);
  });

  it("主题色变化时同步写入虹彩色标", async () => {
    const store = useSettingsStore();
    const before = document.documentElement.style.getPropertyValue("--ff-iri-b");

    store.updateThemeColor("#13C2C2");
    await nextTick();

    const after = document.documentElement.style.getPropertyValue("--ff-iri-b");
    expect(before).toMatch(/^#[0-9a-f]{6}$/i);
    expect(after).toMatch(/^#[0-9a-f]{6}$/i);
    expect(after).not.toBe(before);
  });
});
