import { defaultSettings } from "@/settings";
import { SidebarColor, ThemeMode } from "@/enums/settings/theme-enum";
import type { LayoutMode } from "@/enums/settings/layout-enum";
import { applyTheme, generateThemeColors, toggleDarkMode, toggleSidebarColor } from "@/utils/theme";
import { STORAGE_KEYS } from "@/constants";

type SidebarColorScheme = AppSettings["sidebarColorScheme"];

// 🎯 设置项类型定义
interface SettingsState {
  // 界面显示设置
  settingsVisible: boolean;
  showTagsView: boolean;
  showAppLogo: boolean;
  showWatermark: boolean;

  // 布局设置
  layout: LayoutMode;
  sidebarColorScheme: SidebarColorScheme;

  // 主题设置
  theme: ThemeMode;
  themeColor: string;
}

interface SettingsRefMap {
  showTagsView: Ref<SettingsState["showTagsView"]>;
  showAppLogo: Ref<SettingsState["showAppLogo"]>;
  showWatermark: Ref<SettingsState["showWatermark"]>;
  sidebarColorScheme: Ref<SettingsState["sidebarColorScheme"]>;
  layout: Ref<SettingsState["layout"]>;
}

// 🎯 设置项写入值和 key 保持关联，避免通用更新入口绕过类型约束
type SettingValue<K extends keyof SettingsRefMap> =
  SettingsRefMap[K] extends Ref<infer Value> ? Value : never;

export const useSettingsStore = defineStore("setting", () => {
  // 设置面板可见性
  const settingsVisible = ref<boolean>(false);

  // 是否显示标签页视图
  const showTagsView = useStorage<boolean>(
    STORAGE_KEYS.SHOW_TAGS_VIEW,
    defaultSettings.showTagsView
  );

  // 是否显示应用Logo
  const showAppLogo = useStorage<boolean>(STORAGE_KEYS.SHOW_APP_LOGO, defaultSettings.showAppLogo);

  // 是否显示水印
  const showWatermark = useStorage<boolean>(
    STORAGE_KEYS.SHOW_WATERMARK,
    defaultSettings.showWatermark
  );

  // 侧边栏配色方案
  const sidebarColorScheme = useStorage<SidebarColorScheme>(
    STORAGE_KEYS.SIDEBAR_COLOR_SCHEME,
    defaultSettings.sidebarColorScheme
  );

  // 布局模式
  const layout = useStorage<LayoutMode>(STORAGE_KEYS.LAYOUT, defaultSettings.layout as LayoutMode);

  // 主题颜色
  const themeColor = useStorage<string>(STORAGE_KEYS.THEME_COLOR, defaultSettings.themeColor);

  // 主题模式（亮色/暗色）
  const theme = useStorage<ThemeMode>(STORAGE_KEYS.THEME, defaultSettings.theme);

  // 设置项映射，用于统一管理
  const settingsMap: SettingsRefMap = {
    showTagsView,
    showAppLogo,
    showWatermark,
    sidebarColorScheme,
    layout,
  } as const;

  // 监听主题变化，自动应用样式
  watch(
    [theme, themeColor],
    ([newTheme, newThemeColor]: [ThemeMode, string]) => {
      toggleDarkMode(newTheme === ThemeMode.DARK);
      const colors = generateThemeColors(newThemeColor, newTheme);
      applyTheme(colors);
    },
    { immediate: true }
  );

  // 监听侧边栏配色变化
  watch(
    [sidebarColorScheme],
    ([newSidebarColorScheme]) => {
      toggleSidebarColor(newSidebarColorScheme === SidebarColor.CLASSIC_BLUE);
    },
    { immediate: true }
  );

  // 通用设置更新方法
  function updateSetting<K extends keyof SettingsRefMap>(key: K, value: SettingValue<K>): void {
    const setting = settingsMap[key] as Ref<SettingValue<K>>;
    setting.value = value;
  }

  // 主题更新方法
  function updateTheme(newTheme: ThemeMode): void {
    theme.value = newTheme;
  }

  function updateThemeColor(newColor: string): void {
    themeColor.value = newColor;
  }

  function updateSidebarColorScheme(newScheme: SidebarColorScheme): void {
    sidebarColorScheme.value = newScheme;
  }

  function updateLayout(newLayout: LayoutMode): void {
    layout.value = newLayout;
  }

  // 设置面板控制
  function toggleSettingsPanel(): void {
    settingsVisible.value = !settingsVisible.value;
  }

  function showSettingsPanel(): void {
    settingsVisible.value = true;
  }

  function hideSettingsPanel(): void {
    settingsVisible.value = false;
  }

  // 重置所有设置
  function resetSettings(): void {
    showTagsView.value = defaultSettings.showTagsView;
    showAppLogo.value = defaultSettings.showAppLogo;
    showWatermark.value = defaultSettings.showWatermark;
    sidebarColorScheme.value = defaultSettings.sidebarColorScheme;
    layout.value = defaultSettings.layout as LayoutMode;
    themeColor.value = defaultSettings.themeColor;
    theme.value = defaultSettings.theme;
  }

  return {
    // 状态
    settingsVisible,
    showTagsView,
    showAppLogo,
    showWatermark,
    sidebarColorScheme,
    layout,
    themeColor,
    theme,

    // 更新方法
    updateSetting,
    updateTheme,
    updateThemeColor,
    updateSidebarColorScheme,
    updateLayout,

    // 面板控制
    toggleSettingsPanel,
    showSettingsPanel,
    hideSettingsPanel,

    // 重置功能
    resetSettings,
  };
});
