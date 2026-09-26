import type { LocationQueryRaw, RouteRecordRaw } from "vue-router";
import { useAppStore, usePermissionStore } from "@/store";
import { getMixTopMenuPath } from "../../modes/mix/useMixLayoutState";

function visibleChildrenOf(route: RouteRecordRaw) {
  return (route.children ?? []).filter((child) => !child.meta?.hidden);
}

/** 一级菜单下是否需要第二列/左栏：只有一个可见子菜单时直接当作叶子菜单 */
export function hasSubMenus(route: RouteRecordRaw) {
  return Boolean(route.meta?.alwaysShow) || visibleChildrenOf(route).length > 1;
}

/**
 * 一级菜单（mix 顶部菜单、双列布局的图标栏）的共用逻辑：
 * 生成一级菜单列表、同步当前激活的一级菜单，以及点击后跳到它下面第一个可访问的页面
 */
export function useTopMenuNavigation() {
  const router = useRouter();
  const route = useRoute();
  const appStore = useAppStore();
  const permissionStore = usePermissionStore();

  const activeTopMenuPath = computed(() => appStore.activeTopMenuPath);

  // 只有一个可见子菜单时，一级菜单直接显示子菜单的标题和图标
  const topMenus = computed(() =>
    permissionStore.routes
      .filter((item) => !item.meta?.hidden)
      .map((item) => {
        const visibleChildren = visibleChildrenOf(item);
        if (item.meta?.alwaysShow || visibleChildren.length !== 1) {
          return item;
        }
        const [onlyChild] = visibleChildren;
        return {
          ...item,
          meta: {
            ...item.meta,
            title: onlyChild.meta?.title || item.meta?.title,
            icon: onlyChild.meta?.icon || item.meta?.icon,
          },
        };
      })
  );

  const activeTopMenu = computed(() =>
    permissionStore.routes.find((item) => item.path === activeTopMenuPath.value)
  );

  function activate(topMenuPath: string) {
    if (topMenuPath === appStore.activeTopMenuPath) return;
    appStore.activeTopMenu(topMenuPath);
    permissionStore.setMixLayoutSideMenus(topMenuPath);
  }

  // 递归找到第一个叶子菜单并跳转
  function navigateToFirstLeaf(menus: RouteRecordRaw[]) {
    const [firstMenu] = menus.filter((menu) => !menu.meta?.hidden);
    if (!firstMenu) return;

    if (firstMenu.children?.length) {
      navigateToFirstLeaf(firstMenu.children as RouteRecordRaw[]);
    } else if (firstMenu.name) {
      router.push({
        name: firstMenu.name,
        query:
          typeof firstMenu.meta?.params === "object"
            ? (firstMenu.meta.params as LocationQueryRaw)
            : undefined,
      });
    }
  }

  function selectTopMenu(topMenuPath: string) {
    activate(topMenuPath);
    navigateToFirstLeaf(permissionStore.mixLayoutSideMenus);
  }

  // 首次渲染和路由变化（例如从页签切换）时，让一级菜单和左栏跟随当前页面
  onMounted(() => {
    appStore.activeTopMenu(getMixTopMenuPath(route.path));
    permissionStore.setMixLayoutSideMenus(getMixTopMenuPath(route.path));
  });
  watch(
    () => route.path,
    (path) => {
      if (path) activate(getMixTopMenuPath(path));
    }
  );

  return { activeTopMenu, activeTopMenuPath, selectTopMenu, topMenus };
}
