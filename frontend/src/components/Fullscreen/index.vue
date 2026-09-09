<template>
  <button
    type="button"
    class="navbar-icon-button"
    :aria-label="t(isFullscreen ? 'navbar.exitFullscreen' : 'navbar.enterFullscreen')"
    :aria-pressed="isFullscreen"
    @click="toggle"
  >
    <AppIcon :name="isFullscreen ? 'minimize' : 'maximize'" :size="18" />
  </button>
</template>

<script setup lang="ts">
const { isFullscreen, toggle } = useFullscreen();
const { t } = useI18n();
import AppIcon from "@/components/AppIcon/index.vue";
</script>

<style lang="scss" scoped></style>
