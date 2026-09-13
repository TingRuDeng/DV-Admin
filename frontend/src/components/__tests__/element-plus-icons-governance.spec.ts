import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { ElInput } from "element-plus";
import { ArrowDown, InfoFilled, View } from "@/components/AppIcon/element-plus-icons";

describe("Element Plus icon compatibility", () => {
  it("resolves built-in icon imports through Lucide aliases", () => {
    for (const [component, iconClass] of [
      [ArrowDown, "lucide-chevron-down"],
      [InfoFilled, "lucide-info"],
      [View, "lucide-eye"],
    ] as const) {
      const wrapper = mount(component);
      expect(wrapper.get("svg").classes()).toContain(iconClass);
      wrapper.unmount();
    }
  });

  it("renders real Element Plus inputs with default icons and clears their values", async () => {
    const wrapper = mount(ElInput, { props: { modelValue: "Search", clearable: true } });
    await wrapper.trigger("mouseenter");
    expect(wrapper.get("input").element.value).toBe("Search");
    await wrapper.get(".el-input__clear").trigger("click");
    expect(wrapper.emitted("update:modelValue")).toEqual([[""]]);
    wrapper.unmount();
  });
});
