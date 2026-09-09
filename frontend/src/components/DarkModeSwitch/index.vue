<template>
  <el-dropdown trigger="click" @command="handleDarkChange">
    <AppIcon :name="settingsStore.theme === ThemeMode.DARK ? 'moon' : 'sun'" :size="19" />
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="item in theneList"
          :key="item.value"
          :command="item.value"
          :disabled="settingsStore.theme === item.value"
        >
          <AppIcon :name="item.icon" :size="16" />
          {{ item.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>
<script setup lang="ts">
import { useSettingsStore } from "@/store";
import { ThemeMode } from "@/enums";
import AppIcon from "@/components/AppIcon/index.vue";

const { t } = useI18n();
const settingsStore = useSettingsStore();

const theneList = [
  { label: t("login.light"), value: ThemeMode.LIGHT, icon: "sun" },
  { label: t("login.dark"), value: ThemeMode.DARK, icon: "moon" },
];

const handleDarkChange = (theme: ThemeMode) => {
  settingsStore.updateTheme(theme);
};
</script>
