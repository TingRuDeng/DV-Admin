import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { CircleHelp, FileText, GitBranch, Pencil, Search, UserRound } from "@lucide/vue";
import AppIcon from "@/components/AppIcon/index.vue";
import { APP_ICON_NAMES, resolveAppIcon } from "@/components/AppIcon/icon-map";

describe("AppIcon", () => {
  it("resolves known names and falls back for unknown names", () => {
    expect(resolveAppIcon("search")).toBe(Search);
    expect(resolveAppIcon("unknown")).toBe(CircleHelp);
  });

  it.each([
    ["el-icon-User", UserRound],
    ["i-svg:user", UserRound],
    ["file-text", FileText],
    ["pencil", Pencil],
    ["github", GitBranch],
  ] as const)("resolves legacy or semantic icon name %s", (name, expected) => {
    expect(resolveAppIcon(name)).toBe(expected);
  });

  it("provides a Lucide component for every picker icon", () => {
    APP_ICON_NAMES.forEach((name) => {
      if (name !== "circle-help") {
        expect(resolveAppIcon(name), name).not.toBe(CircleHelp);
      }
    });
  });

  it("keeps decorative icons hidden from assistive technology", () => {
    const wrapper = mount(AppIcon, { props: { name: "search" } });

    expect(wrapper.attributes("aria-hidden")).toBe("true");
    expect(wrapper.find("svg").exists()).toBe(true);
  });
});
