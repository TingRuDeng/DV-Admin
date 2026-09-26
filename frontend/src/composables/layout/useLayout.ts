import { useAppStore, useSettingsStore } from "@/store";
import { defaultSettings } from "@/settings";
import { LayoutMode } from "@/enums/settings/layout-enum";

/**
 * 布局相关的通用逻辑
 */
export function useLayout() {
  const appStore = useAppStore();
  const settingsStore = useSettingsStore();

  // 是否移动设备
  const isMobile = computed(() => appStore.device === "mobile");

  // 实际渲染的布局：双列布局在移动端退化为左侧布局，直接复用它的抽屉导航
  const currentLayout = computed(() =>
    isMobile.value && settingsStore.layout === LayoutMode.DOUBLE
      ? LayoutMode.LEFT
      : settingsStore.layout
  );

  // 侧边栏展开状态
  const isSidebarOpen = computed(() => appStore.sidebar.opened);

  // 是否显示标签视图
  const isShowTagsView = computed(() => settingsStore.showTagsView);

  // 是否显示设置面板
  const isShowSettings = computed(() => defaultSettings.showSettings);

  // 是否显示Logo
  const isShowLogo = computed(() => settingsStore.showAppLogo);

  // 布局CSS类
  const layoutClass = computed(() => ({
    hideSidebar: !appStore.sidebar.opened,
    openSidebar: appStore.sidebar.opened,
    mobile: appStore.device === "mobile",
    [`layout-${currentLayout.value}`]: true,
    "is-content-maximized": appStore.contentMaximized,
  }));

  /**
   * 处理切换侧边栏的展开/收起状态
   */
  function toggleSidebar() {
    appStore.toggleSidebar();
  }

  /**
   * 关闭侧边栏（移动端）
   */
  function closeSidebar() {
    appStore.closeSideBar();
  }

  return {
    currentLayout,
    isSidebarOpen,
    isShowTagsView,
    isShowSettings,
    isShowLogo,
    isMobile,
    layoutClass,
    toggleSidebar,
    closeSidebar,
  };
}
