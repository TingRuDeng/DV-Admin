<template>
  <div class="ff-login-page">
    <header class="ff-login-page__top">
      <i class="ff-login-page__orb" aria-hidden="true"></i>
      <div class="ff-login-page__actions">
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
    </header>

    <main class="ff-login-page__main" aria-labelledby="login-page-title">
      <h2
        id="login-page-title"
        ref="wordRef"
        class="ff-login-page__word"
        :aria-label="defaultSettings.title"
        :style="wordFit ? { '--word-fit': wordFit } : undefined"
      >
        <span
          v-for="(glyph, index) in titleGlyphs"
          :key="index"
          class="ff-login-page__glyph"
          :style="{ '--i': index }"
          aria-hidden="true"
          v-text="glyph"
        />
      </h2>

      <section class="ff-login-page__slab">
        <transition name="fade-slide" mode="out-in">
          <component :is="formComponents[component]" v-model="component" class="login-form" />
        </transition>
      </section>
    </main>

    <footer class="ff-login-page__version">v{{ defaultSettings.version }}</footer>
  </div>
</template>

<script setup lang="ts">
import { defaultSettings } from "@/settings";
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

// 字标逐字入场。字号按逐字实测宽度缩放到铺满视口宽度（左右各留 padding-left），高度上限交给样式的 min()
const titleGlyphs = [...defaultSettings.title];
const wordRef = ref<HTMLElement>();
const wordFit = ref("");

function fitWord() {
  const word = wordRef.value;
  if (!word) return;
  const style = getComputedStyle(word);
  const glyphWidth = Array.from(word.children).reduce(
    (sum, glyph) => sum + (glyph as HTMLElement).offsetWidth,
    0
  );
  if (!glyphWidth) return;
  const available = word.clientWidth - parseFloat(style.paddingLeft) * 2;
  wordFit.value = `${Math.floor((parseFloat(style.fontSize) * available * 10) / glyphWidth) / 10}px`;
}

useEventListener(window, "resize", fitWord);
onMounted(() => {
  fitWord();
  document.fonts?.ready.then(fitWord);
});
</script>

<style lang="scss" scoped>
.fade-slide-leave-active,
.fade-slide-enter-active {
  transition: all var(--ff-duration-base) var(--ff-ease-out);
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
