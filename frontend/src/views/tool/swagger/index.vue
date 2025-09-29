<template>
  <SwaggerFrame :src="swaggerApi" />
</template>
<script>
import SwaggerFrame from "./components/SwaggerFrame";
export default {
  name: "Swagger",
  components: { SwaggerFrame: SwaggerFrame },
  data() {
    return {
      swaggerApi: import.meta.env.VITE_APP_API_URL + "/swagger/",
    };
  },
};
</script>
