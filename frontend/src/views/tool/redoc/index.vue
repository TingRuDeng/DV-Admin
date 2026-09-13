<template>
  <PageShell class="ff-tool-page">
    <RedocFrame :src="redocApi" />
  </PageShell>
</template>
<script setup>
import PageShell from "@/components/PageShell/index.vue";
import RedocFrame from "./components/RedocFrame.vue";
import { ref } from "vue";
// 明确指定组件名称
defineOptions({
  name: "Redoc",
});

// 使用ref定义响应式数据
const apiVersion = import.meta.env.VITE_APP_API_VERSION || "";
const baseApi = apiVersion ? `/api/${apiVersion}/` : "/api/";
const redocApi = ref(import.meta.env.VITE_APP_API_URL + baseApi + "redoc/");
</script>
