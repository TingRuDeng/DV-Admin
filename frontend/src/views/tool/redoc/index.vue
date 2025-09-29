<template>
  <RedocFrame :src="redocApi" />
</template>
<script setup>
import RedocFrame from "./components/RedocFrame.vue";
import { ref } from "vue";
import { defineOptions } from "vue";

// 明确指定组件名称
defineOptions({
  name: "Redoc",
});

// 使用ref定义响应式数据
const redocApi = ref(import.meta.env.VITE_APP_API_URL + "/redoc/");
</script>
