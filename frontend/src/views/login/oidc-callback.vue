<template>
  <div class="ff-login-page">
    <main class="ff-login-page__main ff-oidc-callback__main" aria-labelledby="oidc-callback-title">
      <section class="ff-login-page__slab ff-oidc-callback">
        <h2 id="oidc-callback-title" class="ff-oidc-callback__title">{{ providerName }}</h2>
        <p v-if="errorMessage" class="ff-oidc-callback__error" role="alert">{{ errorMessage }}</p>
        <p
          v-else
          class="ff-oidc-callback__status"
          role="status"
          :aria-label="t('login.oidcPending')"
        >
          <AppIcon name="loader-circle" :size="22" class="is-loading" />
        </p>
        <el-button v-if="errorMessage" class="login-form__sso-button" @click="backToLogin">
          {{ t("login.oidcBack") }}
        </el-button>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import { useUserStore } from "@/store";
import { createLogger } from "@/utils/logger";
import { resolveSafeRedirect } from "@/utils/safe-redirect";
import { takeOidcFlow } from "./oidc-flow";

defineOptions({ name: "OidcCallback" });

const MESSAGE_FLOW_INVALID = "登录状态无效或已过期，请重新发起单点登录";
const MESSAGE_PROVIDER_DENIED = "身份提供方未完成登录";

const callbackLogger = createLogger("OidcCallback");
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const providerName = import.meta.env.VITE_OIDC_PROVIDER_NAME || t("login.oidcProvider");
const errorMessage = ref("");

function queryText(name: string) {
  const value = route.query[name];
  return typeof value === "string" ? value : "";
}

function backToLogin() {
  router.replace("/login");
}

onMounted(async () => {
  const code = queryText("code");
  const state = queryText("state");
  const iss = queryText("iss");
  const providerError = queryText("error");
  // 授权码只能用一次，也不应留在地址栏、浏览器历史或之后的 Referer 里
  window.history.replaceState(window.history.state, "", route.path);
  const flow = takeOidcFlow();

  if (providerError) {
    errorMessage.value = MESSAGE_PROVIDER_DENIED;
    return;
  }
  // state 必须与本标签页发起时保存的一致，防止把别人的授权码塞进当前会话
  if (!flow || !code || !state || flow.state !== state) {
    errorMessage.value = MESSAGE_FLOW_INVALID;
    return;
  }

  try {
    await userStore.loginWithOidc({
      authorizationCode: code,
      state,
      flowSecret: flow.flowSecret,
      ...(iss ? { iss } : {}),
    });
    await router.replace(resolveSafeRedirect(flow.redirect));
  } catch (error) {
    callbackLogger.error("单点登录失败:", error);
    errorMessage.value =
      error instanceof Error && error.message ? error.message : MESSAGE_FLOW_INVALID;
  }
});
</script>
