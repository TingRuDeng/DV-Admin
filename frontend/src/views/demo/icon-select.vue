<!-- 图标选择器示例 -->
<template>
  <PageShell class="ff-demo-page">
    <div class="ff-demo-page__panel">
      <IconSelect v-model="iconName" />
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import IconSelect from "@/components/IconSelect/index.vue";
const iconName = ref("edit");
</script>
