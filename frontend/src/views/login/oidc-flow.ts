import { STORAGE_KEYS } from "@/constants";
import { Storage } from "@/utils/storage";

/** 一次单点登录在浏览器里保存的上下文，只放 sessionStorage，关闭标签页即失效 */
export interface OidcFlowContext {
  state: string;
  flowSecret: string;
  redirect: string;
}

export function isOidcEnabled(env: Partial<ImportMetaEnv> = import.meta.env) {
  return env.VITE_OIDC_ENABLED === "true";
}

export function saveOidcFlow(context: OidcFlowContext) {
  Storage.sessionSet(STORAGE_KEYS.OIDC_FLOW, context);
}

/** 读取后立即删除，保证同一个 state 在浏览器侧也只能用一次 */
export function takeOidcFlow(): OidcFlowContext | null {
  const context = Storage.sessionGet<Partial<OidcFlowContext> | null>(STORAGE_KEYS.OIDC_FLOW, null);
  Storage.sessionRemove(STORAGE_KEYS.OIDC_FLOW);
  if (
    !context ||
    typeof context.state !== "string" ||
    typeof context.flowSecret !== "string" ||
    typeof context.redirect !== "string"
  ) {
    return null;
  }
  return { state: context.state, flowSecret: context.flowSecret, redirect: context.redirect };
}

/** 跳转到身份提供方；单独导出便于测试替换 */
export function navigateToProvider(url: string) {
  window.location.assign(url);
}
