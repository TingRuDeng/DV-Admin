import { compile } from "sass";
import { resolve } from "node:path";

export function injectStyle(cssText: string) {
  const style = document.createElement("style");
  style.textContent = cssText;
  document.head.appendChild(style);
}

export function compileStyle(path: string) {
  return compile(resolve(process.cwd(), path)).css;
}

export function resetThemeTestDom() {
  document.head.innerHTML = "";
  document.body.innerHTML = "";
  document.documentElement.className = "";
}
