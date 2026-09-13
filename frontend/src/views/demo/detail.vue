<template>
  <PageShell class="ff-demo-page">
    <div class="ff-demo-page__panel demo-detail-panel">
      <div class="demo-detail-row">
        <span>params</span>
        <code>{{ route.params }}</code>
      </div>
      <div class="demo-detail-row">
        <span>query</span>
        <code>{{ route.query }}</code>
      </div>
      <el-input v-model="value" placeholder="缓存测试" />
    </div>
  </PageShell>
</template>
<script lang="ts" setup>
import PageShell from "@/components/PageShell/index.vue";

defineOptions({
  name: "DemoDetail",
});

const route = useRoute();

const value = ref("");
</script>
