<!-- wangEditor富文本编辑器示例 -->
<template>
  <PageShell class="ff-demo-page">
    <div class="ff-demo-page__panel">
      <WangEditor v-model="value" height="400px" />

      <div style="margin-top: 10px">
        <textarea v-model="value" readonly style="width: 100%; height: 200px; outline: none" />
      </div>
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import WangEditor from "@/components/WangEditor/index.vue";

const value = ref("初始化内容");
</script>
