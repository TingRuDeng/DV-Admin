<template>
  <div class="login-container">
    <!-- 右侧切换主题、语言按钮  -->
    <div class="action-bar">
      <el-tooltip :content="t('login.themeToggle')" placement="bottom">
        <CommonWrapper>
          <DarkModeSwitch />
        </CommonWrapper>
      </el-tooltip>
      <el-tooltip :content="t('login.languageToggle')" placement="bottom">
        <CommonWrapper>
          <LangSelect size="text-20px" />
        </CommonWrapper>
      </el-tooltip>
    </div>
    <!-- 登录页主体 -->
    <div flex-1 flex-center>
      <div class="login-card">
        <div w-full flex flex-col items-center>
          <!-- logo -->
          <div class="cyber-logo">
            <div class="logo-glow"></div>
            <div class="logo-glass">
              <span class="logo-letter">DV</span>
            </div>
          </div>

          <!-- 标题 -->
          <h2 class="login-title">
            <el-badge :value="`v ${defaultSettings.version}`" type="primary">
              {{ defaultSettings.title }}
            </el-badge>
          </h2>

          <!-- 组件切换 -->
          <transition name="fade-slide" mode="out-in">
            <component :is="formComponents[component]" v-model="component" class="login-form" />
          </transition>
        </div>
      </div>
      <!-- 登录页底部版权 -->
      <el-text size="small" class="login-footer">
        Copyright © 2021 - 2025 {{ defaultSettings.title }} All Rights Reserved.
      </el-text>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defaultSettings } from "@/settings";
import CommonWrapper from "@/components/CommonWrapper/index.vue";
import DarkModeSwitch from "@/components/DarkModeSwitch/index.vue";

type LayoutMap = "login" | "register" | "resetPwd";

const t = useI18n().t;

const component = ref<LayoutMap>("login"); // 切换显示的组件
const formComponents = {
  login: defineAsyncComponent(() => import("./components/Login.vue")),
  register: defineAsyncComponent(() => import("./components/Register.vue")),
  resetPwd: defineAsyncComponent(() => import("./components/ResetPwd.vue")),
};
</script>

<style lang="scss" scoped>
@use "@/styles/pages/login";

/* fade-slide */
.fade-slide-leave-active,
.fade-slide-enter-active {
  transition: all 0.3s;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
