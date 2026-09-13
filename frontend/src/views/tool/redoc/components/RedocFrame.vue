<template>
  <div v-loading="loading" class="redoc-container">
    <iframe :src="src" class="redoc-iframe" title="ReDoc API 文档" @load="handleIframeLoad" />
  </div>
</template>
<script setup>
import { ref } from "vue";
// 明确指定组件名称，避免与其他组件冲突
defineOptions({
  name: "RedocFrame",
});

// Define props without storing them in an unused variable
defineProps({
  src: {
    type: String,
    required: true,
  },
});

const loading = ref(true);

// 监听iframe加载完成
const handleIframeLoad = () => {
  loading.value = false;
};
</script>
<style scoped>
.redoc-container {
  width: 100%;
  height: 100%;
  min-height: 100%;
  overflow: hidden;
  background: var(--ff-shell-surface);
}

.redoc-iframe {
  width: 100%;
  height: 100%;
  overflow: auto;
  border: none;
  transition: opacity 0.3s ease;
}
</style>
