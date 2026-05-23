<template>
  <section class="config-section">
    <el-divider>{{ t("settings.theme") }}</el-divider>

    <div class="flex-center">
      <el-switch
        v-model="isDark"
        active-icon="Moon"
        inactive-icon="Sunny"
        class="theme-switch"
        @change="handleThemeChange"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ThemeMode } from "@/enums";
import { useSettingsStore } from "@/store";

const { t } = useI18n();
const settingsStore = useSettingsStore();

const isDark = ref<boolean>(settingsStore.theme === ThemeMode.DARK);

function handleThemeChange(isDarkMode: string | number | boolean) {
  settingsStore.updateTheme(isDarkMode ? ThemeMode.DARK : ThemeMode.LIGHT);
}

function syncLocalState() {
  isDark.value = settingsStore.theme === ThemeMode.DARK;
}

defineExpose({
  syncLocalState,
});
</script>

<style lang="scss" scoped>
.config-section {
  margin-bottom: 24px;
}

.theme-switch {
  transform: scale(1.2);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.25);
  }
}
</style>
