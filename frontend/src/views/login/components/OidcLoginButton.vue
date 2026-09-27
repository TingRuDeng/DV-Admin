<template>
  <div class="login-form__sso">
    <span class="login-form__divider" aria-hidden="true" />
    <el-tooltip v-if="!enabled" :content="t('login.oidcDisabledTip')" placement="top">
      <span class="login-form__sso-button--wrap">
        <el-button disabled class="login-form__sso-button">
          <AppIcon name="lock" :size="15" class="login-form__sso-button-icon" />
          {{ providerName }}
        </el-button>
      </span>
    </el-tooltip>
    <el-button v-else :loading="loading" class="login-form__sso-button" @click="startOidcLogin">
      {{ providerName }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
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
    oidcLogger.error("发起单点登录失败:", error);
    loading.value = false;
  }
}
</script>
