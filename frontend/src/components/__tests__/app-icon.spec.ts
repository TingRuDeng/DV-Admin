import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { CircleHelp, Search } from "lucide-vue-next";
import AppIcon from "@/components/AppIcon/index.vue";
import { resolveAppIcon } from "@/components/AppIcon/icon-map";

describe("AppIcon", () => {
  it("resolves known names and falls back for unknown names", () => {
    expect(resolveAppIcon("search")).toBe(Search);
    expect(resolveAppIcon("unknown")).toBe(CircleHelp);
  });

  it("keeps decorative icons hidden from assistive technology", () => {
    const wrapper = mount(AppIcon, { props: { name: "search" } });

    expect(wrapper.attributes("aria-hidden")).toBe("true");
    expect(wrapper.find("svg").exists()).toBe(true);
  });
});
