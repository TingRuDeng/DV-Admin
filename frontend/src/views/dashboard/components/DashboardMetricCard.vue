<template>
  <article :class="['dashboard-metric', `dashboard-metric--${accent}`]">
    <div class="dashboard-metric__icon">
      <AppIcon :name="icon" :size="18" />
    </div>
    <div class="dashboard-metric__body">
      <span class="dashboard-metric__label">{{ label }}</span>
      <strong class="dashboard-metric__value">{{ value }}</strong>
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
  }>(),
  {
    accent: "neutral",
  }
);
</script>
