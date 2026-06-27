<template>
  <el-breadcrumb class="flex-y-center">
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="item.path">
      <span
        v-if="item.redirect === 'noredirect' || index === breadcrumbs.length - 1"
        class="color-gray-400"
      >
        {{ translateRouteTitle(item.meta.title) }}
      </span>
      <a v-else @click.prevent="handleLink(item)">
        {{ translateRouteTitle(item.meta.title) }}
      </a>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import type { RouteLocationMatched, RouteLocationRaw } from "vue-router";
import { compile } from "path-to-regexp";
import router from "@/router";
import { translateRouteTitle } from "@/utils/i18n";
import { createLogger } from "@/utils/logger";

type BreadcrumbRoute = Pick<RouteLocationMatched, "path" | "name" | "meta" | "redirect">;

const DASHBOARD_BREADCRUMB: BreadcrumbRoute = {
  path: "/dashboard",
  name: "Dashboard",
  meta: { title: "dashboard" },
  redirect: undefined,
};

const breadcrumbLogger = createLogger("Breadcrumb");
const currentRoute = useRoute();
const pathCompile = (path: string) => {
  const { params } = currentRoute;
  const toPath = compile(path);
  return toPath(params);
};

const breadcrumbs = ref<BreadcrumbRoute[]>([]);

function getBreadcrumb() {
  let matched: BreadcrumbRoute[] = currentRoute.matched.filter(
    (item) => item.meta && item.meta.title
  );
  const first = matched[0];
  if (!isDashboard(first)) {
    matched = [DASHBOARD_BREADCRUMB].concat(matched);
  }
  breadcrumbs.value = matched.filter((item) => {
    return item.meta && item.meta.title && item.meta.breadcrumb !== false;
  });
}

function isDashboard(route: BreadcrumbRoute | undefined) {
  const name = route && route.name;
  if (!name) {
    return false;
  }
  return name.toString().trim().toLocaleLowerCase() === "Dashboard".toLocaleLowerCase();
}

function handleLink(item: BreadcrumbRoute) {
  const { redirect, path } = item;
  if (redirect) {
    router.push(resolveRedirect(redirect)).catch((err) => {
      breadcrumbLogger.warn("面包屑重定向跳转失败:", err);
    });
    return;
  }
  router.push(pathCompile(path)).catch((err) => {
    breadcrumbLogger.warn("面包屑路径跳转失败:", err);
  });
}

function resolveRedirect(redirect: NonNullable<BreadcrumbRoute["redirect"]>): RouteLocationRaw {
  if (typeof redirect === "function") {
    return redirect(currentRoute);
  }
  return redirect;
}

watch(
  () => currentRoute.path,
  (path) => {
    if (path.startsWith("/redirect/")) {
      return;
    }
    getBreadcrumb();
  }
);

onBeforeMount(() => {
  getBreadcrumb();
});
</script>

<style lang="scss" scoped>
// 覆盖 element-plus 的样式
.el-breadcrumb__inner,
.el-breadcrumb__inner a {
  font-weight: 400 !important;
}
</style>
