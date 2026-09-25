import { afterEach, describe, expect, it } from "vitest";
import { ThemeMode } from "@/enums/settings/theme-enum";
import { defaultSettings, themeColorPresets } from "@/settings";
import { applyIridescence, contrastRatio, generateIridescentStops } from "@/utils/theme";

// Liquid Chrome 原型里的三段色标
const PROTOTYPE_STOPS = {
  [ThemeMode.DARK]: ["#bfd7ff", "#d9c2ff", "#ffd6c2"],
  [ThemeMode.LIGHT]: ["#2f4fd0", "#6e36d6", "#b4411a"],
};

const HEX_PATTERN = /^#[0-9a-f]{6}$/i;

function channelDistance(hexA: string, hexB: string) {
  const channels = (hex: string) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const a = channels(hexA);
  const b = channels(hexB);
  return Math.max(...a.map((value, index) => Math.abs(value - b[index])));
}

describe("generateIridescentStops", () => {
  afterEach(() => {
    document.documentElement.removeAttribute("style");
  });

  it.each([ThemeMode.DARK, ThemeMode.LIGHT] as const)(
    "默认预设在 %s 模式下贴近原型色标",
    (mode) => {
      const stops = generateIridescentStops(defaultSettings.themeColor, mode);

      [stops.a, stops.b, stops.c].forEach((stop, index) => {
        expect(channelDistance(stop, PROTOTYPE_STOPS[mode][index])).toBeLessThanOrEqual(6);
      });
    }
  );

  it("深色模式配深色文字，浅色模式配白字", () => {
    expect(generateIridescentStops("#6E36D6", ThemeMode.DARK).onIri).toBe("#0b0b10");
    expect(generateIridescentStops("#6E36D6", ThemeMode.LIGHT).onIri).toBe("#ffffff");
  });

  it("所有预设在两种模式下都输出合法色值且对比度不低于 4.5:1", () => {
    expect(themeColorPresets).toHaveLength(10);

    for (const mode of [ThemeMode.DARK, ThemeMode.LIGHT]) {
      for (const preset of themeColorPresets) {
        const stops = generateIridescentStops(preset, mode);

        for (const stop of [stops.a, stops.b, stops.c]) {
          expect(stop, `${mode} ${preset}`).toMatch(HEX_PATTERN);
          expect(
            contrastRatio(stop, stops.onIri),
            `${mode} ${preset} ${stop}`
          ).toBeGreaterThanOrEqual(4.5);
        }
      }
    }
  });

  it("色标跟随预设色相变化", () => {
    const violet = generateIridescentStops("#6E36D6", ThemeMode.LIGHT);
    const cyan = generateIridescentStops("#13C2C2", ThemeMode.LIGHT);

    expect(cyan.b).not.toBe(violet.b);
  });

  it("applyIridescence 把色标写到根元素", () => {
    applyIridescence({ a: "#111111", b: "#222222", c: "#333333", onIri: "#ffffff" });
    const style = document.documentElement.style;

    expect(style.getPropertyValue("--ff-iri-a")).toBe("#111111");
    expect(style.getPropertyValue("--ff-iri-b")).toBe("#222222");
    expect(style.getPropertyValue("--ff-iri-c")).toBe("#333333");
    expect(style.getPropertyValue("--ff-on-iri")).toBe("#ffffff");
  });
});
