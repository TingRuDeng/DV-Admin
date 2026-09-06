<template>
  <button
    type="button"
    class="navbar-icon-button"
    :aria-label="t(isFullscreen ? 'navbar.exitFullscreen' : 'navbar.enterFullscreen')"
    :aria-pressed="isFullscreen"
    @click="toggle"
  >
    <div :class="`i-svg:` + (isFullscreen ? 'fullscreen-exit' : 'fullscreen')" aria-hidden="true" />
  </button>
</template>

<script setup lang="ts">
const { isFullscreen, toggle } = useFullscreen();
const { t } = useI18n();
</script>

<style lang="scss" scoped></style>
