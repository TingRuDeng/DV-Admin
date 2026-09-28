<template>
  <PageShell class="dashboard-page">
    <DashboardHero
      :name="displayName"
      :avatar="userStore.userInfo.avatar"
      :current-time="currentTime"
    />

    <section class="dashboard-metrics" aria-label="工作空间概览">
      <DashboardMetricCard
        label="今日操作"
        :value="stats?.todayCount ?? '-'"
        icon="scroll-text"
        accent="coral"
        :loading="statsLoading"
      />
      <DashboardMetricCard
        label="本周操作"
        :value="stats?.weekCount ?? '-'"
        icon="layout-dashboard"
        accent="blue"
        :loading="statsLoading"
      />
      <DashboardMetricCard
        label="未读通知"
        :value="unreadCount"
        icon="notification"
        accent="neutral"
        :loading="noticeLoading"
      />
    </section>

    <DashboardQuickActions :items="quickActions" @navigate="handleNavigate" />

    <DashboardRecentPages :recent-pages="recentPages" @navigate="handleNavigate" />
  </PageShell>
</template>

<script setup lang="ts">
import type { RouteRecordRaw } from "vue-router";
import { useRouter } from "vue-router";
import PageShell from "@/components/PageShell/index.vue";
import { useLayoutMenu } from "@/composables/layout/useLayoutMenu";
import { useUserStore } from "@/store/modules/user-store";
import { useTagsViewStore } from "@/store/modules/tags-view-store";
import { translateRouteTitle } from "@/utils/i18n";
import { hasAppIcon, normalizeMenuIconName } from "@/components/AppIcon/icon-map";
import LogAPI from "@/api/system/log-api";
import NoticeAPI from "@/api/system/notice-api";
import DashboardHero from "./components/DashboardHero.vue";
import DashboardMetricCard from "./components/DashboardMetricCard.vue";
import DashboardQuickActions, {
  type DashboardQuickAction,
} from "./components/DashboardQuickActions.vue";
import DashboardRecentPages from "./components/DashboardRecentPages.vue";

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

// 访问统计
const stats = ref<import("@/api/system/log-api").LogVisitStats | null>(null);
const statsLoading = ref(false);

// 未读通知数
const unreadCount = ref<number | string>("-");
const noticeLoading = ref(false);

onMounted(async () => {
  // 并行加载统计数据和未读通知数
  statsLoading.value = true;
  noticeLoading.value = true;
  const hasLogPerm = userStore.userInfo.perms.includes("system:logs:query");
  const [statsResult, noticeResult] = await Promise.allSettled([
    hasLogPerm ? LogAPI.getVisitStats() : Promise.reject(new Error("no perm")),
    NoticeAPI.getMyNoticePage({ pageNum: 1, pageSize: 1, isRead: 0 }),
  ]);
  if (statsResult.status === "fulfilled") {
    stats.value = statsResult.value;
  }
  statsLoading.value = false;
  if (noticeResult.status === "fulfilled") {
    unreadCount.value = noticeResult.value.total;
  }
  noticeLoading.value = false;
});

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

// 最近访问：从页签历史里取，排除首页，最多 6 条，最近的在前
const tagsViewStore = useTagsViewStore();
const recentPages = computed<DashboardQuickAction[]>(() =>
  [...tagsViewStore.visitedViews]
    .filter((tag) => tag.path !== "/dashboard" && !tag.affix)
    .reverse()
    .slice(0, 6)
    .map((tag) => {
      const rawIcon = typeof tag.icon === "string" ? tag.icon : "";
      const icon = rawIcon ? normalizeMenuIconName(rawIcon) : "clock";
      return {
        title: translateRouteTitle(tag.title ?? "") || tag.title || "",
        path: tag.path,
        icon: hasAppIcon(icon) ? icon : "clock",
      };
    })
);

function handleNavigate(path: string) {
  void router.push(path);
}
</script>
