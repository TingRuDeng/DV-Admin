import { LayoutMode } from "@/enums";
import { SidebarColor, ThemeMode } from "@/enums/settings/theme-enum";

export const NAVBAR_ACTIONS_WHITE_TEXT_CLASS = "navbar-actions--white-text";
export const NAVBAR_ACTIONS_DARK_TEXT_CLASS = "navbar-actions--dark-text";

export interface NavbarActionsClassOptions {
  theme: ThemeMode;
  sidebarColorScheme: AppSettings["sidebarColorScheme"];
  layout: LayoutMode;
}

export type NavbarActionsTextClass =
  | typeof NAVBAR_ACTIONS_WHITE_TEXT_CLASS
  | typeof NAVBAR_ACTIONS_DARK_TEXT_CLASS;

/**
 * 统一判定导航栏右侧动作区的文字颜色 class，避免主题分支散落在组件内。
 */
export function resolveNavbarActionsTextClass({
  theme,
  sidebarColorScheme,
  layout,
}: NavbarActionsClassOptions): NavbarActionsTextClass {
  if (theme === ThemeMode.DARK) {
    return NAVBAR_ACTIONS_WHITE_TEXT_CLASS;
  }

  const isHeaderLayout = layout === LayoutMode.TOP || layout === LayoutMode.MIX;
  const isClassicBlueHeader =
    theme === ThemeMode.LIGHT && isHeaderLayout && sidebarColorScheme === SidebarColor.CLASSIC_BLUE;

  return isClassicBlueHeader ? NAVBAR_ACTIONS_WHITE_TEXT_CLASS : NAVBAR_ACTIONS_DARK_TEXT_CLASS;
}
