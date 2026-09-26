<template>
  <div v-if="enabled" class="login-form__sso">
    <span class="login-form__divider" aria-hidden="true" />
    <el-button :loading="loading" class="login-form__sso-button" @click="startOidcLogin">
      {{ providerName }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import AuthAPI from "@/api/auth-api";
import { createLogger } from "@/utils/logger";
import { resolveSafeRedirect } from "@/utils/safe-redirect";
import { isOidcEnabled, navigateToProvider, saveOidcFlow } from "../oidc-flow";

const oidcLogger = createLogger("OidcLogin");
const { t } = useI18n();
const route = useRoute();

const enabled = isOidcEnabled();
const providerName = import.meta.env.VITE_OIDC_PROVIDER_NAME || t("login.oidcProvider");
const loading = ref(false);

async function startOidcLogin() {
  loading.value = true;
  try {
    const { authorizationUrl, state, flowSecret } = await AuthAPI.oidcAuthorize();
    saveOidcFlow({ state, flowSecret, redirect: resolveSafeRedirect(route.query.redirect) });
    navigateToProvider(authorizationUrl);
  } catch (error) {
    // 接口错误已由请求拦截器提示，这里只恢复按钮
    oidcLogger.error("发起单点登录失败:", error);
    loading.value = false;
  }
}
</script>
