<template>
  <div v-loading="loading" class="redoc-container" :style="{ height: containerHeight }">
    <iframe ref="redocIframe" :src="src" class="redoc-iframe" @load="handleIframeLoad" />
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { defineOptions } from "vue";

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
const redocIframe = ref(null);
const containerHeight = ref("");

// 计算容器高度
const calculateHeight = () => {
  const windowHeight = document.documentElement.clientHeight;
  containerHeight.value = `${windowHeight - 94.5}px`;
};

// 监听iframe加载完成
const handleIframeLoad = () => {
  loading.value = false;
};

// 处理窗口大小变化
const handleResize = () => {
  calculateHeight();
};

onMounted(() => {
  calculateHeight();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
});
</script>
<style scoped>
.redoc-container {
  width: 100%;
  overflow: hidden;
}

.redoc-iframe {
  width: 100%;
  height: 100%;
  overflow: auto;
  border: none;
  transition: opacity 0.3s ease;
}
</style>
