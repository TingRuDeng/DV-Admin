import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import DashboardMetricCard from "../DashboardMetricCard.vue";
import DashboardQuickActions from "../DashboardQuickActions.vue";

describe("dashboard components", () => {
  it("renders a real metric value", () => {
    const wrapper = mount(DashboardMetricCard, {
      props: {
        label: "角色",
        value: 3,
        icon: "users-round",
        accent: "blue",
      },
    });

    expect(wrapper.find(".dashboard-metric__value").text()).toBe("3");
  });

  it("emits the selected shortcut path", async () => {
    const wrapper = mount(DashboardQuickActions, {
      props: { items: [{ title: "用户管理", path: "/system/user", icon: "users" }] },
    });

    await wrapper.find("button").trigger("click");

    expect(wrapper.emitted("navigate")?.[0]).toEqual(["/system/user"]);
  });

  it("shows a concise empty state when no shortcuts exist", () => {
    const wrapper = mount(DashboardQuickActions, { props: { items: [] } });

    expect(wrapper.find(".dashboard-actions__empty").text()).toBe("暂无可访问入口");
  });
});
