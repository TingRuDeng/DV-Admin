<template>
  <div>
    <h3 text-center m-0 mb-20px>{{ t("login.resetPassword") }}</h3>
    <el-form
      ref="formRef"
      :model="model"
      :rules="rules"
      :validate-on-rule-change="false"
      size="large"
    >
      <el-form-item prop="username">
        <el-input v-model.trim="model.username" :placeholder="t('login.username')" />
      </el-form-item>
      <el-form-item prop="email">
        <el-input v-model.trim="model.email" :placeholder="t('login.email')" />
      </el-form-item>
      <el-form-item v-if="enableCaptcha" prop="captchaCode">
        <div flex w-full gap-10px>
          <el-input v-model.trim="model.captchaCode" :placeholder="t('login.captchaCode')" />
          <button
            type="button"
            class="captcha-refresh captcha-refresh--compact"
            :aria-label="t('login.captchaRefresh')"
            @click="getCaptcha"
          >
            <img v-if="captchaBase64" :src="captchaBase64" :alt="t('login.captchaAlt')" />
            <AppIcon v-else name="refresh-cw" :size="18" />
          </button>
        </div>
      </el-form-item>
      <el-form-item prop="emailCode">
        <div flex w-full gap-10px>
          <el-input v-model.trim="model.emailCode" :placeholder="t('login.emailCode')" />
          <el-button :disabled="emailCountdown > 0 || emailLoading" @click="sendEmailCode">
            {{ emailCountdown > 0 ? `${emailCountdown}s` : t("login.sendEmailCode") }}
          </el-button>
        </div>
      </el-form-item>
      <el-form-item prop="newPassword">
        <el-input
          v-model="model.newPassword"
          type="password"
          show-password
          :placeholder="t('login.newPassword')"
        />
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input
          v-model="model.confirmPassword"
          type="password"
          show-password
          :placeholder="t('login.message.password.confirm')"
        />
      </el-form-item>
      <el-form-item>
        <el-button :loading="loading" type="warning" class="w-full" @click="submit">
          {{ t("login.resetPassword") }}
        </el-button>
      </el-form-item>
    </el-form>
    <div flex-center gap-10px>
      <el-text>{{ t("login.thinkOfPasswd") }}</el-text>
      <el-link type="primary" underline="never" @click="toLogin">{{ t("login.login") }}</el-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FormInstance, FormRules } from "element-plus";
import { useI18n } from "vue-i18n";
import AuthAPI, { type ResetPasswordRequest } from "@/api/auth-api";
import { defaultSettings } from "@/settings";
import AppIcon from "@/components/AppIcon/index.vue";

const { t } = useI18n();
const emit = defineEmits(["update:modelValue"]);
const toLogin = () => emit("update:modelValue", "login");
const enableCaptcha = defaultSettings.enableCaptcha;
const formRef = ref<FormInstance>();
const loading = ref(false);
const emailLoading = ref(false);
const emailCountdown = ref(0);
const captchaBase64 = ref("");
let captchaKey = "";
let emailTimer: ReturnType<typeof setInterval> | undefined;
const model = ref({
  username: "",
  email: "",
  captchaCode: "",
  emailCode: "",
  newPassword: "",
  confirmPassword: "",
});
const rules = computed<FormRules<typeof model.value>>(() => ({
  username: [{ required: true, trigger: "blur", message: t("login.message.username.required") }],
  email: [
    { required: true, type: "email", trigger: "blur", message: t("login.message.email.required") },
  ],
  captchaCode: [
    { required: enableCaptcha, trigger: "blur", message: t("login.message.captchaCode.required") },
  ],
  emailCode: [{ required: true, trigger: "blur", message: t("login.message.emailCode.required") }],
  newPassword: [{ required: true, trigger: "blur", message: t("login.message.password.required") }],
  confirmPassword: [
    { required: true, trigger: "blur", message: t("login.message.password.required") },
    {
      validator: (_rule, value: unknown) => value === model.value.newPassword,
      trigger: "blur",
      message: t("login.message.password.inconformity"),
    },
  ],
}));

onMounted(() => enableCaptcha && getCaptcha());
async function getCaptcha() {
  const data = await AuthAPI.getCaptcha();
  captchaKey = data.captchaKey;
  captchaBase64.value = data.captchaBase64;
}
async function sendEmailCode() {
  try {
    await formRef.value?.validateField(["email", "captchaCode"]);
    emailLoading.value = true;
    await AuthAPI.sendEmailCode({
      purpose: "reset_password",
      email: model.value.email,
      captchaKey,
      captchaCode: model.value.captchaCode,
    });
    emailCountdown.value = 60;
    emailTimer = setInterval(() => {
      emailCountdown.value -= 1;
      if (emailCountdown.value <= 0 && emailTimer) clearInterval(emailTimer);
    }, 1000);
    ElMessage.success(t("login.emailCodeSent"));
  } finally {
    emailLoading.value = false;
  }
}
async function submit() {
  const valid = await formRef.value?.validate();
  if (!valid) return;
  loading.value = true;
  try {
    await AuthAPI.resetPassword({
      username: model.value.username,
      email: model.value.email,
      emailCode: model.value.emailCode,
      newPassword: model.value.newPassword,
      confirmPassword: model.value.confirmPassword,
      captchaKey,
      captchaCode: model.value.captchaCode,
      purpose: "reset_password",
    } satisfies ResetPasswordRequest);
    ElMessage.success(t("login.resetSuccess"));
    toLogin();
  } finally {
    loading.value = false;
  }
}
onUnmounted(() => emailTimer && clearInterval(emailTimer));
</script>
