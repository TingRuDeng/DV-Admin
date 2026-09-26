import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { onMounted } from "vue";
import AuthAPI from "@/api/auth-api";
import { STORAGE_KEYS } from "@/constants";
import { isOidcEnabled, navigateToProvider } from "../../oidc-flow";
import OidcLoginButton from "../OidcLoginButton.vue";

vi.mock("@/api/auth-api", () => ({ default: { oidcAuthorize: vi.fn() } }));
vi.mock("@/utils/logger", () => ({ createLogger: () => ({ error: vi.fn() }) }));
vi.mock("../../oidc-flow", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../oidc-flow")>()),
  navigateToProvider: vi.fn(),
}));

const route = { query: {} as Record<string, unknown> };

function renderButton() {
  return mount(OidcLoginButton, {
    global: {
      stubs: {
        ElButton: {
          props: { loading: Boolean },
          emits: ["click"],
          template: `<button :aria-busy="loading" @click="$emit('click')"><slot /></button>`,
        },
      },
    },
  });
}

beforeEach(() => {
  vi.stubGlobal("useI18n", () => ({ t: (key: string) => key }));
  vi.stubGlobal("useRoute", () => route);
  vi.stubGlobal("onMounted", onMounted);
  route.query = {};
  sessionStorage.clear();
  vi.mocked(AuthAPI.oidcAuthorize).mockReset();
  vi.mocked(navigateToProvider).mockReset();
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("单点登录入口", () => {
  it("只有显式开启时才启用", () => {
    expect(isOidcEnabled({ VITE_OIDC_ENABLED: "true" })).toBe(true);
    expect(isOidcEnabled({ VITE_OIDC_ENABLED: "false" })).toBe(false);
    expect(isOidcEnabled({})).toBe(false);
  });

  it("未开启时不渲染任何内容", () => {
    vi.stubEnv("VITE_OIDC_ENABLED", "false");
    expect(renderButton().find("button").exists()).toBe(false);
  });

  it("按钮文字优先使用环境变量，默认使用 i18n 文案", () => {
    vi.stubEnv("VITE_OIDC_ENABLED", "true");
    vi.stubEnv("VITE_OIDC_PROVIDER_NAME", "");
    expect(renderButton().get("button").text()).toBe("login.oidcProvider");
    vi.stubEnv("VITE_OIDC_PROVIDER_NAME", "Keycloak");
    expect(renderButton().get("button").text()).toBe("Keycloak");
  });

  it("点击后保存 state、流程密钥和安全跳转地址，再跳转到身份提供方", async () => {
    vi.stubEnv("VITE_OIDC_ENABLED", "true");
    route.query = { redirect: "/system/users?page=2" };
    vi.mocked(AuthAPI.oidcAuthorize).mockResolvedValue({
      authorizationUrl: "https://idp.example/authorize?state=s1",
      state: "s1",
      flowSecret: "secret-1",
    });

    const wrapper = renderButton();
    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(JSON.parse(sessionStorage.getItem(STORAGE_KEYS.OIDC_FLOW)!)).toEqual({
      state: "s1",
      flowSecret: "secret-1",
      redirect: "/system/users?page=2",
    });
    expect(navigateToProvider).toHaveBeenCalledWith("https://idp.example/authorize?state=s1");
  });

  it("外部跳转地址回退为首页，发起失败时恢复按钮且不跳转", async () => {
    vi.stubEnv("VITE_OIDC_ENABLED", "true");
    route.query = { redirect: "https://evil.example" };
    vi.mocked(AuthAPI.oidcAuthorize)
      .mockResolvedValueOnce({
        authorizationUrl: "https://idp.example/a",
        state: "s",
        flowSecret: "f",
      })
      .mockRejectedValueOnce(new Error("未启用单点登录"));

    const wrapper = renderButton();
    await wrapper.get("button").trigger("click");
    await flushPromises();
    expect(JSON.parse(sessionStorage.getItem(STORAGE_KEYS.OIDC_FLOW)!).redirect).toBe("/");

    vi.mocked(navigateToProvider).mockClear();
    await wrapper.get("button").trigger("click");
    await flushPromises();
    expect(navigateToProvider).not.toHaveBeenCalled();
    expect(wrapper.get("button").attributes("aria-busy")).toBe("false");
  });
});
