import { ThemeMode } from "@/enums";

// 辅助函数：将十六进制颜色转换为 RGB
function hexToRgb(hex: string): [number, number, number] {
  const bigint = parseInt(hex.slice(1), 16);
  return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
}

// 辅助函数：将 RGB 转换为十六进制颜色
function rgbToHex(r: number, g: number, b: number): string {
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

// 辅助函数：调整颜色亮度
/** function adjustBrightness(hex: string, factor: number, theme: string): string {
  const rgb = hexToRgb(hex);
  // 是否是暗黑模式
  const isDarkMode = theme === "dark" ? 0 : 255;
  const newRgb = rgb.map((val) =>
    Math.max(0, Math.min(255, Math.round(val + (isDarkMode - val) * factor)))
  ) as [number, number, number];
  return rgbToHex(...newRgb);
} */

/**
 * 加深颜色值
 * @param {String} color 颜色值字符串
 * @param {Number} level 加深的程度，限0-1之间
 * @returns {String} 返回处理后的颜色值
 */
export function getDarkColor(color: string, level: number): string {
  const rgb = hexToRgb(color);
  for (let i = 0; i < 3; i++) rgb[i] = Math.round(20.5 * level + rgb[i] * (1 - level));
  return rgbToHex(rgb[0], rgb[1], rgb[2]);
}

/**
 * 变浅颜色值
 * @param {String} color 颜色值字符串
 * @param {Number} level 加深的程度，限0-1之间
 * @returns {String} 返回处理后的颜色值
 */
export const getLightColor = (color: string, level: number): string => {
  const rgb = hexToRgb(color);
  for (let i = 0; i < 3; i++) rgb[i] = Math.round(255 * level + rgb[i] * (1 - level));
  return rgbToHex(rgb[0], rgb[1], rgb[2]);
};

/**
 * 生成主题色
 * @param primary 主题色
 * @param theme 主题类型
 */
export function generateThemeColors(primary: string, theme: ThemeMode) {
  const colors: Record<string, string> = {
    primary,
  };

  // 生成浅色变体
  for (let i = 1; i <= 9; i++) {
    colors[`primary-light-${i}`] =
      theme === ThemeMode.LIGHT
        ? `${getLightColor(primary, i / 10)}`
        : `${getDarkColor(primary, i / 10)}`;
  }

  // 生成深色变体
  colors["primary-dark-2"] =
    theme === ThemeMode.LIGHT ? `${getLightColor(primary, 0.2)}` : `${getDarkColor(primary, 0.3)}`;

  return colors;
}

export function applyTheme(colors: Record<string, string>) {
  const el = document.documentElement;

  Object.entries(colors).forEach(([key, value]) => {
    el.style.setProperty(`--el-color-${key}`, value);
  });

  // 确保主题色立即生效，强制重新渲染
  requestAnimationFrame(() => {
    // 触发样式重新计算
    el.style.setProperty("--theme-update-trigger", Date.now().toString());
  });
}

export interface IridescentStops {
  a: string;
  b: string;
  c: string;
  onIri: string;
}

type Rgb = [number, number, number];

// 两种模式下三段色标的 OKLCH 目标：h 为相对预设色色相的偏移，数值按 Liquid Chrome 原型标定
const IRI_TARGETS = {
  [ThemeMode.DARK]: {
    h: [-32, 10, 115],
    l: [0.875, 0.855, 0.905],
    c: [0.061, 0.087, 0.053],
    onIri: "#0b0b10",
  },
  [ThemeMode.LIGHT]: {
    h: [-25, 0, 105],
    l: [0.49, 0.5, 0.53],
    c: [0.2, 0.225, 0.16],
    onIri: "#ffffff",
  },
} as const;
const MIN_IRI_CONTRAST = 4.5;

const toLinear = (c: number) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const fromLinear = (c: number) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);

function hexToLinearRgb(hex: string): Rgb {
  return hexToRgb(hex).map((v) => toLinear(v / 255)) as Rgb;
}

function linearRgbToHex(rgb: Rgb): string {
  const [r, g, b] = rgb.map((v) => Math.round(Math.min(1, Math.max(0, fromLinear(v))) * 255));
  return rgbToHex(r, g, b);
}

function relativeLuminance([r, g, b]: Rgb): number {
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function contrastRatio(hexA: string, hexB: string): number {
  const la = relativeLuminance(hexToLinearRgb(hexA));
  const lb = relativeLuminance(hexToLinearRgb(hexB));
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

function hueOf(hex: string): number {
  const [r, g, b] = hexToLinearRgb(hex);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  const a = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
  const bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
  return ((Math.atan2(bb, a) * 180) / Math.PI + 360) % 360;
}

function oklchToLinearRgb(lightness: number, chroma: number, hue: number): Rgb {
  const rad = (hue * Math.PI) / 180;
  const a = chroma * Math.cos(rad);
  const b = chroma * Math.sin(rad);
  const l = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s = (lightness - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [
    4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
  ];
}

const inGamut = (rgb: Rgb) => rgb.every((v) => v >= -1e-4 && v <= 1 + 1e-4);

// 超出 sRGB 时先降彩度，保持明度和色相不变
function gamutMappedHex(lightness: number, chroma: number, hue: number): string {
  let low = 0;
  let high = chroma;
  if (!inGamut(oklchToLinearRgb(lightness, high, hue))) {
    for (let i = 0; i < 20; i++) {
      const mid = (low + high) / 2;
      if (inGamut(oklchToLinearRgb(lightness, mid, hue))) low = mid;
      else high = mid;
    }
    high = low;
  }
  return linearRgbToHex(oklchToLinearRgb(lightness, high, hue));
}

/**
 * 由预设色推导虹彩三段色标
 *
 * 以预设色的 OKLCH 色相为中心取三个色标，深色模式为粉彩配深色文字，浅色模式为饱和色配白字；
 * 超出 sRGB 时降彩度，与 on-iri 文字对比度不足 4.5:1 时逐步调整明度。
 */
export function generateIridescentStops(primary: string, theme: ThemeMode): IridescentStops {
  const mode = theme === ThemeMode.DARK ? ThemeMode.DARK : ThemeMode.LIGHT;
  const target = IRI_TARGETS[mode];
  const step = mode === ThemeMode.DARK ? 0.01 : -0.01;
  const hue = hueOf(primary);

  const [a, b, c] = target.h.map((offset, index) => {
    const stopHue = (hue + offset + 360) % 360;
    let lightness: number = target.l[index];
    let hex = gamutMappedHex(lightness, target.c[index], stopHue);
    while (contrastRatio(hex, target.onIri) < MIN_IRI_CONTRAST && lightness > 0 && lightness < 1) {
      lightness += step;
      hex = gamutMappedHex(lightness, target.c[index], stopHue);
    }
    return hex;
  });

  return { a, b, c, onIri: target.onIri };
}

export function applyIridescence(stops: IridescentStops) {
  const el = document.documentElement;
  el.style.setProperty("--ff-iri-a", stops.a);
  el.style.setProperty("--ff-iri-b", stops.b);
  el.style.setProperty("--ff-iri-c", stops.c);
  el.style.setProperty("--ff-on-iri", stops.onIri);
}

/**
 * 切换暗黑模式
 *
 * @param isDark 是否启用暗黑模式
 */
export function toggleDarkMode(isDark: boolean) {
  if (isDark) {
    document.documentElement.classList.add(ThemeMode.DARK);
  } else {
    document.documentElement.classList.remove(ThemeMode.DARK);
  }
}

/**
 * 切换浅色主题下的侧边栏颜色方案
 *
 * @param isBlue 布尔值，表示是否开启深蓝色侧边栏颜色方案
 */
export function toggleSidebarColor(isBuleSidebar: boolean) {
  if (isBuleSidebar) {
    document.documentElement.classList.add("sidebar-color-blue");
  } else {
    document.documentElement.classList.remove("sidebar-color-blue");
  }
}
