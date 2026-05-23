import type { LayoutMode } from "@/enums";

export interface LayoutOption {
  value: LayoutMode;
  label: string;
  className: string;
}

export type SidebarColorScheme = AppSettings["sidebarColorScheme"];
export type RadioGroupChangeValue = string | number | boolean | undefined;
