import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PageShell from "@/components/PageShell/index.vue";
import FilterPanel from "@/components/FilterPanel/index.vue";
import DataPanel from "@/components/DataPanel/index.vue";

describe("page shell components", () => {
  it("renders PageShell with the shared wrapper class", () => {
    const wrapper = mount(PageShell, {
      slots: { default: "<div class='inner'>content</div>" },
    });

    expect(wrapper.classes()).toContain("ff-page-shell");
    expect(wrapper.find(".inner").exists()).toBe(true);
  });

  it("renders FilterPanel as a semantic shell", () => {
    const wrapper = mount(FilterPanel, {
      slots: { default: "<form class='filter-body'></form>" },
    });

    expect(wrapper.classes()).toContain("ff-filter-panel");
    expect(wrapper.find(".filter-body").exists()).toBe(true);
  });

  it("renders DataPanel title, actions, body, and footer slots", () => {
    const wrapper = mount(DataPanel, {
      props: { title: "用户数据" },
      slots: {
        actions: "<button class='action'>新增</button>",
        default: "<div class='table-body'></div>",
        footer: "<div class='pager'></div>",
      },
    });

    expect(wrapper.find(".ff-data-panel__title").text()).toContain("用户数据");
    expect(wrapper.find(".action").exists()).toBe(true);
    expect(wrapper.find(".table-body").exists()).toBe(true);
    expect(wrapper.find(".pager").exists()).toBe(true);
  });
});
