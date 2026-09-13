<template>
  <div>
    <h3 text-center m-0 mb-20px>{{ t("login.reg") }}</h3>
    <el-form
      ref="formRef"
      :model="model"
      :rules="rules"
      :validate-on-rule-change="false"
      size="large"
    >
      <!-- 用户名 -->
      <el-form-item prop="username">
        <el-input v-model.trim="model.username" :placeholder="t('login.username')">
          <template #prefix>
            <AppIcon name="user-round" :size="17" />
          </template>
        </el-input>
      </el-form-item>

      <!-- 密码 -->
      <el-tooltip :visible="isCapsLock" :content="t('login.capsLock')" placement="right">
        <el-form-item prop="password">
          <el-input
            v-model="model.password"
            :placeholder="t('login.password')"
            type="password"
            show-password
            @keyup="checkCapsLock"
            @keyup.enter="submit"
          >
            <template #prefix>
              <AppIcon name="lock" :size="17" />
            </template>
          </el-input>
        </el-form-item>
      </el-tooltip>

      <el-tooltip :visible="isCapsLock" :content="t('login.capsLock')" placement="right">
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="model.confirmPassword"
            :placeholder="t('login.message.password.confirm')"
            type="password"
            show-password
            @keyup="checkCapsLock"
            @keyup.enter="submit"
          >
            <template #prefix>
              <AppIcon name="lock" :size="17" />
            </template>
          </el-input>
        </el-form-item>
      </el-tooltip>

      <el-form-item prop="email">
        <el-input v-model.trim="model.email" :placeholder="t('login.email')">
          <template #prefix><AppIcon name="mail" :size="17" /></template>
        </el-input>
      </el-form-item>

      <!-- 验证码 - 根据配置显示 -->
      <el-form-item v-if="enableCaptcha" prop="captchaCode">
        <div flex>
          <el-input
            v-model.trim="model.captchaCode"
            :placeholder="t('login.captchaCode')"
            @keyup.enter="submit"
          >
            <template #prefix>
              <AppIcon name="captcha" :size="17" />
            </template>
          </el-input>
          <button
            type="button"
            class="captcha-refresh captcha-refresh--compact ml-10px"
            :aria-label="t('login.captchaRefresh')"
            @click="getCaptcha"
          >
            <AppIcon v-if="codeLoading" name="loader-circle" :size="18" class="is-loading" />

            <img
              v-else
              object-cover
              border-rd-4px
              p-1px
              shadow="[0_0_0_1px_var(--el-border-color)_inset]"
              :src="captchaBase64"
              :alt="t('login.captchaAlt')"
            />
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

      <el-form-item>
        <div class="flex-y-center w-full gap-10px">
          <el-checkbox v-model="isRead">{{ t("login.agree") }}</el-checkbox>
          <el-link type="primary" underline="never">{{ t("login.userAgreement") }}</el-link>
        </div>
      </el-form-item>

      <!-- 注册按钮 -->
      <el-form-item>
        <el-button :loading="loading" type="success" class="w-full" @click="submit">
          {{ t("login.register") }}
        </el-button>
      </el-form-item>
    </el-form>
    <div flex-center gap-10px>
      <el-text size="default">{{ t("login.haveAccount") }}</el-text>
      <el-link type="primary" underline="never" @click="toLogin">{{ t("login.login") }}</el-link>
    </div>
  </div>
</template>
<script setup lang="ts">
import type { FormInstance, FormRules } from "element-plus";
import { useI18n } from "vue-i18n";
import AuthAPI, { type LoginFormData, type RegisterRequest } from "@/api/auth-api";
import { defaultSettings } from "@/settings";
import { getLoginDefaultCredentials } from "./login-defaults";
import AppIcon from "@/components/AppIcon/index.vue";

const { t } = useI18n();

const emit = defineEmits(["update:modelValue"]);
const toLogin = () => emit("update:modelValue", "login");

// 是否启用验证码
const enableCaptcha = defaultSettings.enableCaptcha;

// 如果启用了验证码，组件挂载时获取验证码
onMounted(() => {
  if (enableCaptcha) {
    getCaptcha();
  }
});

const formRef = ref<FormInstance>();
const loading = ref(false); // 按钮 loading 状态
const isCapsLock = ref(false); // 是否大写锁定
const captchaBase64 = ref(); // 验证码图片Base64字符串
const isRead = ref(false);

interface Model extends LoginFormData {
  confirmPassword: string;
  email: string;
  emailCode: string;
}

const defaultCredentials = getLoginDefaultCredentials();

const model = ref<Model>({
  username: defaultCredentials.username,
  password: defaultCredentials.password,
  confirmPassword: "",
  email: "",
  emailCode: "",
  captchaKey: "",
  captchaCode: "",
  rememberMe: false,
});

const rules = computed(() => {
  const registerRules: FormRules<Model> = {
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
    confirmPassword: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.password.required"),
      },
      {
        validator: (_rule, value: unknown) => {
          return typeof value === "string" && value === model.value.password;
        },
        trigger: "blur",
        message: t("login.message.password.inconformity"),
      },
    ],
    email: [
      {
        required: true,
        type: "email",
        trigger: "blur",
        message: t("login.message.email.required"),
      },
    ],
    emailCode: [
      { required: true, trigger: "blur", message: t("login.message.emailCode.required") },
    ],
  };

  // 只有启用了验证码时才添加验证码的验证规则
  if (enableCaptcha) {
    registerRules.captchaCode = [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.captchaCode.required"),
      },
    ];
  }

  // 重要：确保返回规则对象
  return registerRules;
});

// 获取验证码
const codeLoading = ref(false);
const emailLoading = ref(false);
const emailCountdown = ref(0);
let emailTimer: ReturnType<typeof setInterval> | undefined;
function getCaptcha() {
  codeLoading.value = true;
  AuthAPI.getCaptcha()
    .then((data) => {
      model.value.captchaKey = data.captchaKey;
      captchaBase64.value = data.captchaBase64;
    })
    .finally(() => (codeLoading.value = false));
}

// 检查输入大小写
function checkCapsLock(event: KeyboardEvent) {
  // 防止浏览器密码自动填充时报错
  if (event instanceof KeyboardEvent) {
    isCapsLock.value = event.getModifierState("CapsLock");
  }
}

const submit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;
  loading.value = true;
  try {
    await AuthAPI.register({
      purpose: "register",
      username: model.value.username,
      email: model.value.email,
      password: model.value.password,
      confirmPassword: model.value.confirmPassword,
      emailCode: model.value.emailCode,
      captchaKey: model.value.captchaKey,
      captchaCode: model.value.captchaCode,
    } satisfies RegisterRequest);
    ElMessage.success(t("login.registerSuccess"));
    toLogin();
  } finally {
    loading.value = false;
  }
};

async function sendEmailCode() {
  try {
    await formRef.value?.validateField(["email", "captchaCode"]);
  } catch {
    return;
  }
  emailLoading.value = true;
  try {
    await AuthAPI.sendEmailCode({
      purpose: "register",
      email: model.value.email,
      captchaKey: model.value.captchaKey,
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

onUnmounted(() => emailTimer && clearInterval(emailTimer));
</script>
