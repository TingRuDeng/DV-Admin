<template>
  <PageShell class="ff-demo-page">
    <div class="ff-demo-page__panel demo-route-param-panel">
      <span class="demo-route-param-panel__label">路由参数 type</span>
      <code>{{ query }}</code>
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";

defineOptions({
  name: "Other",
  inheritAttrs: false,
});
import { useRoute } from "vue-router";

// 获取query参数
const query = useRoute().query.type as string;
</script>
