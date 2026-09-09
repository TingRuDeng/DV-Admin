<template>
  <div class="login-container">
    <div class="login-ambient login-ambient--coral" aria-hidden="true"></div>
    <div class="login-ambient login-ambient--blue" aria-hidden="true"></div>
    <div class="login-grid" aria-hidden="true"></div>

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

    <main class="login-layout" aria-labelledby="login-page-title">
      <section class="login-art" aria-hidden="true">
        <div class="login-art__topline">
          <span>DV-ADMIN</span>
          <span>ACCESS / 01</span>
        </div>
        <div class="login-art__title">
          <span>CONTROL</span>
          <em>ROOM</em>
        </div>
        <div class="login-art__line"></div>
        <div class="login-art__footer">
          <span>RBAC / PLATFORM</span>
          <span>LOCAL SESSION</span>
        </div>
      </section>

      <section class="login-card">
        <div class="login-card__header">
          <div class="cyber-logo" aria-hidden="true">
            <div class="logo-glow"></div>
            <div class="logo-glass">
              <AppIcon name="command" :size="30" :stroke-width="1.8" />
            </div>
          </div>
          <div>
            <p class="login-kicker">Workspace access</p>
            <h2 id="login-page-title">进入工作区</h2>
          </div>
        </div>

        <transition name="fade-slide" mode="out-in">
          <component :is="formComponents[component]" v-model="component" class="login-form" />
        </transition>
      </section>
    </main>

    <footer class="login-footer">
      {{ defaultSettings.title }} · {{ defaultSettings.version }}
    </footer>
  </div>
</template>

<script setup lang="ts">
import { defaultSettings } from "@/settings";
import AppIcon from "@/components/AppIcon/index.vue";
import CommonWrapper from "@/components/CommonWrapper/index.vue";
import DarkModeSwitch from "@/components/DarkModeSwitch/index.vue";
import LangSelect from "@/components/LangSelect/index.vue";

type LayoutMap = "login" | "register" | "resetPwd";

const { t } = useI18n();
const component = shallowRef<LayoutMap>("login");
const formComponents = {
  login: defineAsyncComponent(() => import("./components/Login.vue")),
  register: defineAsyncComponent(() => import("./components/Register.vue")),
  resetPwd: defineAsyncComponent(() => import("./components/ResetPwd.vue")),
};
</script>

<style lang="scss" scoped>
@use "@/styles/pages/login";

.fade-slide-leave-active,
.fade-slide-enter-active {
  transition: all var(--ff-duration-base) var(--ff-ease-spring);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-18px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(18px);
}
</style>
