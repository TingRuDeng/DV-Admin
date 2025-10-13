<template>
  <SwaggerFrame :src="swaggerApi" />
</template>
<script setup lang="ts">
// Import the required component
import SwaggerFrame from "./components/SwaggerFrame.vue";

defineOptions({
  name: "Swagger",
});

const swaggerApi = import.meta.env.VITE_APP_API_URL + "/api/swagger/";
</script>
