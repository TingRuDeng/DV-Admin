<template>
  <PageShell class="dashboard-page">
    <DashboardHero
      :name="displayName"
      :avatar="userStore.userInfo.avatar"
      :current-time="currentTime"
    />

    <section class="dashboard-metrics" :aria-label="t('dashboard.workspaceOverview')">
      <DashboardMetricCard
        :label="t('dashboard.accessibleModules')"
        :value="accessibleModuleCount"
        icon="layout-dashboard"
        accent="coral"
      />
      <DashboardMetricCard
        :label="t('dashboard.roles')"
        :value="userStore.userInfo.roles.length"
        icon="users-round"
        accent="blue"
      />
      <DashboardMetricCard
        :label="t('dashboard.permissions')"
        :value="userStore.userInfo.perms.length"
        icon="shield-check"
        accent="neutral"
      />
    </section>

    <DashboardQuickActions :items="quickActions" @navigate="handleNavigate" />
  </PageShell>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import PageShell from "@/components/PageShell/index.vue";
import { useLayoutMenu } from "@/composables/layout/useLayoutMenu";
import { useUserStore } from "@/store/modules/user-store";
import { isExternal } from "@/utils";
import DashboardHero from "./components/DashboardHero.vue";
import DashboardMetricCard from "./components/DashboardMetricCard.vue";
import DashboardQuickActions from "./components/DashboardQuickActions.vue";
import { collectDashboardActions } from "./dashboard-route-actions";

defineOptions({
  name: "Dashboard",
  inheritAttrs: false,
});

const router = useRouter();
const userStore = useUserStore();
const { routes } = useLayoutMenu();
const { t } = useI18n();
const currentTime = useDateFormat(useNow(), "HH:mm");

const displayName = computed(
  () => userStore.userInfo.name || userStore.userInfo.username || t("dashboard.operator")
);

const dashboardActions = computed(() => collectDashboardActions(routes.value));
const quickActions = computed(() => dashboardActions.value.slice(0, 8));
const accessibleModuleCount = computed(() => dashboardActions.value.length);

function handleNavigate(path: string) {
  if (isExternal(path)) {
    window.open(path, "_blank", "noopener,noreferrer");
    return;
  }

  void router.push(path);
}
</script>
