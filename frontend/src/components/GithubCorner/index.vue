<template>
  <a
    href="https://github.com/"
    target="_blank"
    class="github-corner"
    rel="noopener noreferrer"
    aria-label="查看 GitHub 源码"
  >
    <AppIcon name="github" :size="28" :stroke-width="1.7" />
  </a>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
</script>

<style scoped>
.github-corner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ff-accent, #ff705c);
  transition:
    color 180ms ease,
    transform 180ms ease;
}

.github-corner:hover,
.github-corner:focus-visible {
  color: var(--ff-accent-strong, #e95645);
  transform: translateY(-2px) rotate(-4deg);
}

.github-corner:focus-visible {
  outline: 2px solid currentcolor;
  outline-offset: 4px;
}
</style>
