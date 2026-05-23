<template>
  <section class="config-section">
    <el-divider>{{ t("settings.interface") }}</el-divider>

    <div class="config-item flex-x-between">
      <span class="text-xs">{{ t("settings.themeColor") }}</span>
      <el-color-picker
        v-model="selectedThemeColor"
        :predefine="colorPresets"
        popper-class="theme-picker-dropdown"
      />
    </div>

    <div class="config-item flex-x-between">
      <span class="text-xs">{{ t("settings.showTagsView") }}</span>
      <el-switch v-model="settingsStore.showTagsView" />
    </div>

    <div class="config-item flex-x-between">
      <span class="text-xs">{{ t("settings.showAppLogo") }}</span>
      <el-switch v-model="settingsStore.showAppLogo" />
    </div>

    <div class="config-item flex-x-between">
      <span class="text-xs">{{ t("settings.showWatermark") }}</span>
      <el-switch v-model="settingsStore.showWatermark" />
    </div>

    <div v-if="!isDark" class="config-item flex-x-between">
      <span class="text-xs">{{ t("settings.sidebarColorScheme") }}</span>
      <el-radio-group v-model="sidebarColor" @change="changeSidebarColor">
        <el-radio :value="SidebarColor.CLASSIC_BLUE">
          {{ t("settings.classicBlue") }}
        </el-radio>
        <el-radio :value="SidebarColor.MINIMAL_WHITE">
          {{ t("settings.minimalWhite") }}
        </el-radio>
      </el-radio-group>
    </div>
  </section>
</template>

<script setup lang="ts">
import { SidebarColor, ThemeMode } from "@/enums";
import { themeColorPresets } from "@/settings";
import { useSettingsStore } from "@/store";
import type { RadioGroupChangeValue, SidebarColorScheme } from "./types";

const { t } = useI18n();
const settingsStore = useSettingsStore();

const colorPresets = themeColorPresets;
const sidebarColor = ref<SidebarColorScheme>(settingsStore.sidebarColorScheme);

const isDark = computed(() => settingsStore.theme === ThemeMode.DARK);
const selectedThemeColor = computed({
  get: () => settingsStore.themeColor,
  set: (value) => settingsStore.updateThemeColor(value),
});

function isSidebarColorScheme(value: RadioGroupChangeValue): value is SidebarColorScheme {
  return value === SidebarColor.CLASSIC_BLUE || value === SidebarColor.MINIMAL_WHITE;
}

function changeSidebarColor(val: RadioGroupChangeValue) {
  if (!isSidebarColorScheme(val)) {
    throw new Error(`不支持的侧边栏配色方案：${String(val)}`);
  }

  settingsStore.updateSidebarColorScheme(val);
}

function syncLocalState() {
  sidebarColor.value = settingsStore.sidebarColorScheme;
}

defineExpose({
  syncLocalState,
});
</script>

<style lang="scss" scoped>
.config-section {
  margin-bottom: 24px;
}

.config-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  transition: all 0.3s ease;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    padding-right: 8px;
    padding-left: 8px;
    margin: 0 -8px;
    background-color: var(--el-fill-color-light);
    border-radius: 6px;
  }
}
</style>
