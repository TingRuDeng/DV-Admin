<template>
  <ProDrawer
    v-model="drawerVisible"
    size="380"
    :title="t('settings.project')"
    :drawer-attrs="{ beforeClose: handleCloseDrawer }"
    class="settings-drawer"
  >
    <div class="settings-content">
      <ThemeSection ref="themeSectionRef" />
      <InterfaceSection ref="interfaceSectionRef" />
      <LayoutSection />
    </div>

    <template #footer>
      <SettingsActions
        :copy-loading="copyLoading"
        :reset-loading="resetLoading"
        @copy="handleCopySettings"
        @reset="handleResetSettings"
      />
    </template>
  </ProDrawer>
</template>

<script setup lang="ts">
import ProDrawer from "@/components/ProDrawer/index.vue";
import { useSettingsStore } from "@/store";
import InterfaceSection from "./InterfaceSection.vue";
import LayoutSection from "./LayoutSection.vue";
import SettingsActions from "./SettingsActions.vue";
import ThemeSection from "./ThemeSection.vue";

const { t } = useI18n();

const settingsStore = useSettingsStore();
const copyLoading = ref(false);
const resetLoading = ref(false);
const themeSectionRef = ref<InstanceType<typeof ThemeSection> | null>(null);
const interfaceSectionRef = ref<InstanceType<typeof InterfaceSection> | null>(null);

const drawerVisible = computed({
  get: () => settingsStore.settingsVisible,
  set: (value) => (settingsStore.settingsVisible = value),
});

/**
 * 复制当前配置
 */
const handleCopySettings = async () => {
  try {
    copyLoading.value = true;

    // 生成配置代码
    const configCode = generateSettingsCode();

    // 复制到剪贴板
    await navigator.clipboard.writeText(configCode);

    // 显示成功消息
    ElMessage.success({
      message: t("settings.copySuccess"),
      duration: 3000,
    });
  } catch {
    ElMessage.error("复制配置失败");
  } finally {
    copyLoading.value = false;
  }
};

/**
 * 重置为默认配置
 */
const handleResetSettings = async () => {
  resetLoading.value = true;

  try {
    settingsStore.resetSettings();
    syncSectionState();

    ElMessage.success(t("settings.resetSuccess"));
  } catch {
    ElMessage.error("重置配置失败");
  } finally {
    resetLoading.value = false;
  }
};

function syncSectionState() {
  themeSectionRef.value?.syncLocalState();
  interfaceSectionRef.value?.syncLocalState();
}

/**
 * 生成配置代码字符串
 */
const generateSettingsCode = (): string => {
  const settings = {
    title: "pkg.name",
    version: "pkg.version",
    showSettings: true,
    showTagsView: settingsStore.showTagsView,
    showAppLogo: settingsStore.showAppLogo,
    layout: `LayoutMode.${settingsStore.layout.toUpperCase()}`,
    theme: `ThemeMode.${settingsStore.theme.toUpperCase()}`,
    size: "ComponentSize.DEFAULT",
    language: "LanguageEnum.ZH_CN",
    themeColor: `"${settingsStore.themeColor}"`,
    showWatermark: settingsStore.showWatermark,
    watermarkContent: "pkg.name",
    sidebarColorScheme: `SidebarColor.${settingsStore.sidebarColorScheme.toUpperCase().replace("-", "_")}`,
  };

  return `const defaultSettings: AppSettings = {
  title: ${settings.title},
  version: ${settings.version},
  showSettings: ${settings.showSettings},
  showTagsView: ${settings.showTagsView},
  showAppLogo: ${settings.showAppLogo},
  layout: ${settings.layout},
  theme: ${settings.theme},
  size: ${settings.size},
  language: ${settings.language},
  themeColor: ${settings.themeColor},
  showWatermark: ${settings.showWatermark},
  watermarkContent: ${settings.watermarkContent},
  sidebarColorScheme: ${settings.sidebarColorScheme},
};`;
};

/**
 * 关闭抽屉前的回调
 */
const handleCloseDrawer = () => {
  settingsStore.settingsVisible = false;
};
</script>

<style lang="scss" scoped>
/* 设置抽屉样式 */
.settings-drawer {
  :deep(.el-drawer__body) {
    position: relative;
    height: 100%;
    padding: 0;
    overflow: hidden;
  }
}

/* 设置内容区域 */
.settings-content {
  height: calc(100vh - 120px); /* 减去头部和底部按钮的高度 */
  padding: 20px;
  overflow-y: auto;
}
</style>
