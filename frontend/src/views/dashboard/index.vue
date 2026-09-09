<template>
  <PageShell class="dashboard-page">
    <DashboardHero
      :name="displayName"
      :avatar="userStore.userInfo.avatar"
      :current-time="currentTime"
    />

    <section class="dashboard-metrics" aria-label="工作空间概览">
      <DashboardMetricCard
        label="可访问模块"
        :value="quickActions.length"
        icon="layout-dashboard"
        accent="coral"
      />
      <DashboardMetricCard
        label="角色"
        :value="userStore.userInfo.roles.length"
        icon="users-round"
        accent="blue"
      />
      <DashboardMetricCard
        label="权限"
        :value="userStore.userInfo.perms.length"
        icon="shield-check"
        accent="neutral"
      />
    </section>

    <DashboardQuickActions :items="quickActions" @navigate="handleNavigate" />
  </PageShell>
</template>

<script setup lang="ts">
import type { RouteRecordRaw } from "vue-router";
import { useRouter } from "vue-router";
import PageShell from "@/components/PageShell/index.vue";
import { useLayoutMenu } from "@/composables/layout/useLayoutMenu";
import { useUserStore } from "@/store/modules/user-store";
import { translateRouteTitle } from "@/utils/i18n";
import DashboardHero from "./components/DashboardHero.vue";
import DashboardMetricCard from "./components/DashboardMetricCard.vue";
import DashboardQuickActions, {
  type DashboardQuickAction,
} from "./components/DashboardQuickActions.vue";

defineOptions({
  name: "Dashboard",
  inheritAttrs: false,
});

const router = useRouter();
const userStore = useUserStore();
const { routes } = useLayoutMenu();
const currentTime = useDateFormat(useNow(), "HH:mm");

const displayName = computed(
  () => userStore.userInfo.name || userStore.userInfo.username || "Admin"
);

function joinRoutePath(parentPath: string, path: string) {
  const joined = `${parentPath}/${path}`.replace(/\/+/g, "/");
  return joined.startsWith("/") ? joined : `/${joined}`;
}

function collectQuickActions(routeRecords: RouteRecordRaw[], parentPath = "") {
  const result: DashboardQuickAction[] = [];

  routeRecords.forEach((route) => {
    const meta = route.meta ?? {};
    const fullPath = joinRoutePath(parentPath, route.path);
    const children = route.children ?? [];

    if (children.length > 0) {
      result.push(...collectQuickActions(children, fullPath));
      return;
    }

    if (meta.hidden || fullPath === "/dashboard" || !meta.title) return;

    result.push({
      title: translateRouteTitle(String(meta.title)) ?? String(meta.title),
      path: fullPath,
      icon: typeof meta.icon === "string" ? meta.icon.replace(/^el-icon-/, "") : "menu",
    });
  });

  return result.slice(0, 8);
}

const quickActions = computed(() => collectQuickActions(routes.value));

function handleNavigate(path: string) {
  void router.push(path);
}
</script>
