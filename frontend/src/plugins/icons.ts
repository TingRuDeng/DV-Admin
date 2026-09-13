import type { App } from "vue";
import { resolveAppIcon } from "@/components/AppIcon/icon-map";

const legacyIconNames = [
  "ArrowDown",
  "ArrowLeft",
  "ArrowRight",
  "ArrowUp",
  "CircleClose",
  "CircleCloseFilled",
  "Download",
  "Edit",
  "Eye",
  "Moon",
  "Operation",
  "Plus",
  "Position",
  "RefreshLeft",
  "RefreshRight",
  "Search",
  "Sunny",
  "UploadFilled",
  "View",
  "arrow-left",
  "delete",
  "download",
  "edit",
  "plus",
  "refresh",
  "search",
  "upload",
];

// 保留 Element Plus 的全局图标入口，实际渲染统一落到 Lucide。
export function setupElIcons(app: App<Element>) {
  for (const name of legacyIconNames) {
    app.component(name, resolveAppIcon(name));
  }
}
