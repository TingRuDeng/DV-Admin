<template>
  <section
    v-if="recentPages.length"
    class="dashboard-recent"
    aria-labelledby="dashboard-recent-title"
  >
    <h2 id="dashboard-recent-title" class="dashboard-actions__title">最近访问</h2>
    <div class="dashboard-actions__grid">
      <button
        v-for="(item, index) in recentPages"
        :key="item.path"
        type="button"
        class="dashboard-action"
        :style="{ '--i': index }"
        @click="emit('navigate', item.path)"
      >
        <AppIcon :name="item.icon || 'clock'" :size="22" :stroke-width="1.4" />
        <span class="dashboard-action__title">{{ item.title }}</span>
        <AppIcon name="arrow-up-right" :size="16" class="dashboard-action__arrow" />
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import type { DashboardQuickAction } from "./DashboardQuickActions.vue";

defineProps<{
  recentPages: DashboardQuickAction[];
}>();

const emit = defineEmits<{
  navigate: [path: string];
}>();
</script>
