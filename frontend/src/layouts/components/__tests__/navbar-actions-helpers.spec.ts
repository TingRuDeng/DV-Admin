import { describe, expect, it } from "vitest";
import { LayoutMode } from "@/enums";
import { SidebarColor, ThemeMode } from "@/enums/settings/theme-enum";
import {
  NAVBAR_ACTIONS_DARK_TEXT_CLASS,
  NAVBAR_ACTIONS_WHITE_TEXT_CLASS,
  resolveNavbarActionsTextClass,
} from "../NavBar/components/navbarActionsHelpers";

describe("navbar actions helpers", () => {
  it("暗黑主题下所有布局使用白色文字", () => {
    expect(
      resolveNavbarActionsTextClass({
        theme: ThemeMode.DARK,
        sidebarColorScheme: SidebarColor.MINIMAL_WHITE,
        layout: LayoutMode.LEFT,
      })
    ).toBe(NAVBAR_ACTIONS_WHITE_TEXT_CLASS);
  });

  it("明亮主题顶部布局经典蓝侧边栏使用白色文字", () => {
    expect(
      resolveNavbarActionsTextClass({
        theme: ThemeMode.LIGHT,
        sidebarColorScheme: SidebarColor.CLASSIC_BLUE,
        layout: LayoutMode.TOP,
      })
    ).toBe(NAVBAR_ACTIONS_WHITE_TEXT_CLASS);
  });

  it("明亮主题混合布局经典蓝侧边栏使用白色文字", () => {
    expect(
      resolveNavbarActionsTextClass({
        theme: ThemeMode.LIGHT,
        sidebarColorScheme: SidebarColor.CLASSIC_BLUE,
        layout: LayoutMode.MIX,
      })
    ).toBe(NAVBAR_ACTIONS_WHITE_TEXT_CLASS);
  });

  it("明亮主题左侧布局和极简白侧边栏使用深色文字", () => {
    expect(
      resolveNavbarActionsTextClass({
        theme: ThemeMode.LIGHT,
        sidebarColorScheme: SidebarColor.CLASSIC_BLUE,
        layout: LayoutMode.LEFT,
      })
    ).toBe(NAVBAR_ACTIONS_DARK_TEXT_CLASS);

    expect(
      resolveNavbarActionsTextClass({
        theme: ThemeMode.LIGHT,
        sidebarColorScheme: SidebarColor.MINIMAL_WHITE,
        layout: LayoutMode.TOP,
      })
    ).toBe(NAVBAR_ACTIONS_DARK_TEXT_CLASS);
  });
});
