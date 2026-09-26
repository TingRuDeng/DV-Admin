<template>
  <div>
    <el-form
      ref="loginFormRef"
      :model="loginFormData"
      :rules="loginRules"
      size="large"
      :validate-on-rule-change="false"
    >
      <!-- 用户名 -->
      <el-form-item prop="username">
        <label class="login-field__label" for="login-username-input">
          {{ t("login.username") }}
        </label>
        <el-input
          id="login-username-input"
          v-model.trim="loginFormData.username"
          :aria-label="t('login.username')"
          autocomplete="username"
        />
      </el-form-item>

      <!-- 密码 -->
      <el-tooltip :visible="isCapsLock" :content="t('login.capsLock')" placement="right">
        <el-form-item prop="password">
          <label class="login-field__label" for="login-password-input">
            {{ t("login.password") }}
          </label>
          <el-input
            id="login-password-input"
            v-model="loginFormData.password"
            :aria-label="t('login.password')"
            autocomplete="current-password"
            type="password"
            show-password
            @keyup="checkCapsLock"
            @keyup.enter="handleLoginSubmit"
          />
        </el-form-item>
      </el-tooltip>

      <!-- 验证码 - 根据配置显示 -->
      <el-form-item v-if="enableCaptcha" prop="captchaCode">
        <label class="login-field__label" for="login-captcha-input">
          {{ t("login.captchaCode") }}
        </label>
        <div flex items-center gap-10px w-full>
          <el-input
            id="login-captcha-input"
            v-model.trim="loginFormData.captchaCode"
            :aria-label="t('login.captchaCode')"
            autocomplete="off"
            clearable
            class="flex-1"
            @keyup.enter="handleLoginSubmit"
          />
          <div cursor-pointer h-52px w-120px flex-center @click="getCaptcha">
            <AppIcon v-if="codeLoading" name="loader-circle" :size="20" class="is-loading" />

            <img
              v-else-if="captchaBase64"
              border-rd-16px
              w-full
              h-full
              object-cover
              shadow="[0_0_0_1px_rgba(0,0,0,0.06)_inset]"
              :src="captchaBase64"
              alt="captchaCode"
            />
            <el-text v-else type="info" size="small">点击获取</el-text>
          </div>
        </div>
      </el-form-item>

      <!-- 登录按钮 -->
      <el-form-item>
        <el-button
          :loading="loading"
          type="primary"
          class="login-form__submit"
          @click="handleLoginSubmit"
        >
          {{ t("login.login") }}
        </el-button>
      </el-form-item>
    </el-form>

    <OidcLoginButton />
  </div>
</template>
<script setup lang="ts">
import type { FormInstance, FormRules } from "element-plus";
import AuthAPI, { type LoginFormData } from "@/api/auth-api";
import router from "@/router";
import { useUserStore } from "@/store";
import { AuthStorage } from "@/utils/auth";
import { createLogger } from "@/utils/logger";
import { resolveSafeRedirect } from "@/utils/safe-redirect";
import { defaultSettings } from "@/settings";
import { getLoginDefaultCredentials } from "./login-defaults";
import AppIcon from "@/components/AppIcon/index.vue";
import OidcLoginButton from "./OidcLoginButton.vue";

const loginLogger = createLogger("Login");
const { t } = useI18n();
const userStore = useUserStore();
const route = useRoute();

// 是否启用验证码
const enableCaptcha = defaultSettings.enableCaptcha;

// 如果启用了验证码，组件挂载时获取验证码
onMounted(() => {
  if (enableCaptcha) {
    getCaptcha();
  }
});

const loginFormRef = ref<FormInstance>();
const loading = ref(false);
// 是否大写锁定
const isCapsLock = ref(false);
// 验证码图片Base64字符串
const captchaBase64 = ref();
// 记住我
const rememberMe = AuthStorage.getRememberMe();
const defaultCredentials = getLoginDefaultCredentials();

const loginFormData = ref<LoginFormData>({
  username: defaultCredentials.username,
  password: defaultCredentials.password,
  captchaKey: "",
  captchaCode: "",
  rememberMe,
});

const loginRules = computed(() => {
  const rules: FormRules<LoginFormData> = {
    username: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.username.required"),
      },
    ],
    password: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.password.required"),
      },
    ],
  };

  // 只有启用了验证码时才添加验证码的验证规则
  if (enableCaptcha) {
    rules.captchaCode = [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.captchaCode.required"),
      },
    ];
  }

  return rules;
});

// 获取验证码
const codeLoading = ref(false);
function getCaptcha() {
  codeLoading.value = true;
  AuthAPI.getCaptcha()
    .then((data) => {
      loginFormData.value.captchaKey = data.captchaKey;
      captchaBase64.value = data.captchaBase64;
    })
    .finally(() => (codeLoading.value = false));
}

/**
 * 登录提交
 */
async function handleLoginSubmit() {
  // 1. 表单验证：校验失败时 validate() 会 reject，字段下方已有提示，不当作登录失败处理
  const valid = await loginFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  try {
    loading.value = true;

    // 2. 执行登录
    await userStore.login(loginFormData.value);

    // vue-router 已解码过 query，这里只做站内路径校验，不能再解码
    await router.push(resolveSafeRedirect(route.query.redirect));
  } catch (error) {
    // 4. 统一错误处理
    if (enableCaptcha) {
      getCaptcha(); // 刷新验证码
    }
    loginLogger.error("登录失败:", error);
  } finally {
    loading.value = false;
  }
}

// 检查输入大小写
function checkCapsLock(event: KeyboardEvent) {
  // 防止浏览器密码自动填充时报错
  if (event instanceof KeyboardEvent) {
    isCapsLock.value = event.getModifierState("CapsLock");
  }
}
</script>
