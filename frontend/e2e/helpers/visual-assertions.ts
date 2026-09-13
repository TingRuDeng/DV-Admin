import { expect, type Locator } from "@playwright/test";

/** Check the actual solid fill used by a primary action in the browser. */
export async function expectReadableAction(button: Locator) {
  const contrast = await button.evaluate((element) => {
    const style = getComputedStyle(element);
    const luminance = (color: string) => {
      const channels = color.match(/[\d.]+/g)?.map(Number) ?? [];
      if (channels.length < 3 || (channels[3] !== undefined && channels[3] !== 1)) {
        throw new Error(`Primary action requires an opaque color: ${color}`);
      }
      return channels.slice(0, 3).reduce((sum, channel, index) => {
        const value = channel / 255;
        const linear = value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
        return sum + linear * [0.2126, 0.7152, 0.0722][index];
      }, 0);
    };
    if (style.backgroundImage !== "none") throw new Error("Expected a solid primary action");
    const foreground = luminance(style.color);
    const background = luminance(style.backgroundColor);
    return (Math.max(foreground, background) + 0.05) / (Math.min(foreground, background) + 0.05);
  });
  expect(contrast).toBeGreaterThanOrEqual(4.5);
}
