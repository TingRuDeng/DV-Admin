<template>
  <button
    type="button"
    class="navbar-icon-button theme-toggle"
    :aria-label="t('navbar.themeToggle')"
    :aria-pressed="isDark"
    @click="toggleTheme"
  >
    <AppIcon :name="isDark ? 'moon' : 'sun'" :size="18" class="theme-toggle__icon" />
  </button>
</template>

<script setup lang="ts">
import { computed, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import AppIcon from "@/components/AppIcon/index.vue";
import { ThemeMode } from "@/enums/settings/theme-enum";
import { useSettingsStore } from "@/store";
import { revealRadius, supportsThemeReveal } from "./theme-reveal";

const { t } = useI18n();
const settingsStore = useSettingsStore();
const isDark = computed(() => settingsStore.theme === ThemeMode.DARK);

async function applyNextTheme() {
  settingsStore.updateTheme(isDark.value ? ThemeMode.LIGHT : ThemeMode.DARK);
  // settings-store 的主题 watch 在下一次调度时才写 html.dark，快照前要等它执行完
  await nextTick();
}

// 从点击位置扩散新主题：坐标只在点击这一刻取一次，不跟随指针
function toggleTheme(event: MouseEvent) {
  if (!supportsThemeReveal()) {
    void applyNextTheme();
    return;
  }

  const x = event.clientX || window.innerWidth / 2;
  const y = event.clientY || 0;
  const radius = revealRadius(x, y, window.innerWidth, window.innerHeight);
  const transition = document.startViewTransition(applyNextTheme);

  void transition.ready
    .then(() => {
      document.documentElement.animate(
        { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
        { duration: 450, easing: "ease-in", pseudoElement: "::view-transition-new(root)" }
      );
    })
    .catch(() => {
      // 过渡被中断（例如连续点击）时主题已经切换，不需要再处理
    });
}
</script>
