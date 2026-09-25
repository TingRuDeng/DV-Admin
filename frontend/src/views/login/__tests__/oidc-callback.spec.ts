import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { onMounted } from "vue";
import { STORAGE_KEYS } from "@/constants";
import OidcCallback from "../oidc-callback.vue";

const loginWithOidc = vi.fn();
vi.mock("@/store", () => ({ useUserStore: () => ({ loginWithOidc }) }));
vi.mock("@/utils/logger", () => ({ createLogger: () => ({ error: vi.fn() }) }));

const route = { path: "/oidc/callback", query: {} as Record<string, string> };
const router = { replace: vi.fn(() => Promise.resolve()) };

function saveFlow(state = "s1", redirect = "/system/roles") {
  sessionStorage.setItem(
    STORAGE_KEYS.OIDC_FLOW,
    JSON.stringify({ state, flowSecret: "secret-1", redirect })
  );
}

async function renderCallback(query: Record<string, string>) {
  route.query = query;
  const wrapper = mount(OidcCallback, {
    global: {
      stubs: {
        AppIcon: true,
        ElButton: {
          emits: ["click"],
          template: `<button @click="$emit('click')"><slot /></button>`,
        },
      },
    },
  });
  await flushPromises();
  return wrapper;
}

beforeEach(() => {
  vi.stubGlobal("useI18n", () => ({ t: (key: string) => key }));
  vi.stubGlobal("useRoute", () => route);
  vi.stubGlobal("useRouter", () => router);
  vi.stubGlobal("onMounted", onMounted);
  sessionStorage.clear();
  loginWithOidc.mockReset();
  router.replace.mockClear();
  window.history.replaceState(null, "", "/oidc/callback?code=c1&state=s1");
});

afterEach(() => vi.unstubAllGlobals());

describe("单点登录回调页", () => {
  it("state 一致时带流程密钥兑换授权码，并跳回发起前的页面", async () => {
    saveFlow();
    loginWithOidc.mockResolvedValue(undefined);
    await renderCallback({ code: "c1", state: "s1", iss: "https://idp.example" });

    expect(loginWithOidc).toHaveBeenCalledWith({
      authorizationCode: "c1",
      state: "s1",
      flowSecret: "secret-1",
      iss: "https://idp.example",
    });
    expect(router.replace).toHaveBeenCalledWith("/system/roles");
    expect(window.location.search).toBe("");
    expect(sessionStorage.getItem(STORAGE_KEYS.OIDC_FLOW)).toBeNull();
  });

  it("state 不一致或没有发起记录时不发请求，并提供返回登录", async () => {
    saveFlow("another-state");
    const wrapper = await renderCallback({ code: "c1", state: "s1" });

    expect(loginWithOidc).not.toHaveBeenCalled();
    expect(wrapper.get('[role="alert"]').text()).toContain("登录状态无效或已过期");
    await wrapper.get("button").trigger("click");
    expect(router.replace).toHaveBeenCalledWith("/login");

    sessionStorage.clear();
    await renderCallback({ code: "c1", state: "s1" });
    expect(loginWithOidc).not.toHaveBeenCalled();
  });

  it("身份提供方返回 error 时不兑换，并清掉发起记录", async () => {
    saveFlow();
    const wrapper = await renderCallback({ error: "access_denied", state: "s1" });

    expect(loginWithOidc).not.toHaveBeenCalled();
    expect(wrapper.get('[role="alert"]').text()).toBe("身份提供方未完成登录");
    expect(sessionStorage.getItem(STORAGE_KEYS.OIDC_FLOW)).toBeNull();
  });

  it("兑换失败时显示后端给出的原因且不跳转", async () => {
    saveFlow();
    loginWithOidc.mockRejectedValue(new Error("该账号未开通，请联系管理员"));
    const wrapper = await renderCallback({ code: "c1", state: "s1" });

    expect(wrapper.get('[role="alert"]').text()).toBe("该账号未开通，请联系管理员");
    expect(router.replace).not.toHaveBeenCalled();
  });

  it("发起记录里的跳转地址不安全时回到首页", async () => {
    saveFlow("s1", "//evil.example");
    loginWithOidc.mockResolvedValue(undefined);
    await renderCallback({ code: "c1", state: "s1" });

    expect(router.replace).toHaveBeenCalledWith("/");
  });
});
