<template>
  <article :class="['dashboard-metric', `dashboard-metric--${accent}`]">
    <div class="dashboard-metric__icon">
      <AppIcon :name="icon" :size="18" />
    </div>
    <div class="dashboard-metric__body">
      <span class="dashboard-metric__label">{{ label }}</span>
      <strong class="dashboard-metric__value">
        <span v-if="loading" class="dashboard-metric__skeleton" />
        <template v-else>{{ value }}</template>
      </strong>
    </div>
  </article>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";

withDefaults(
  defineProps<{
    label: string;
    value: string | number;
    icon: string;
    accent?: "coral" | "blue" | "neutral";
    loading?: boolean;
  }>(),
  {
    accent: "neutral",
    loading: false,
  }
);
</script>

<style lang="scss" scoped>
.dashboard-metric__skeleton {
  display: inline-block;
  width: 3rem;
  height: 1.4rem;
  vertical-align: middle;
  background: linear-gradient(
    90deg,
    var(--ff-shell-border) 25%,
    var(--ff-shell-hover) 50%,
    var(--ff-shell-border) 75%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: ff-skeleton-shimmer 1.4s infinite;
}

@keyframes ff-skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .dashboard-metric__skeleton {
    background: var(--ff-shell-border);
    animation: none;
  }
}
</style>
