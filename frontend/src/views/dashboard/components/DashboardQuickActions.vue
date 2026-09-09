<template>
  <section class="dashboard-actions" aria-labelledby="dashboard-actions-title">
    <div class="dashboard-actions__header">
      <div>
        <p class="dashboard-actions__eyebrow">Navigation</p>
        <h2 id="dashboard-actions-title">快捷入口</h2>
      </div>
      <span class="dashboard-actions__count">{{ String(items.length).padStart(2, "0") }}</span>
    </div>

    <div v-if="items.length" class="dashboard-actions__grid">
      <button
        v-for="item in items"
        :key="item.path"
        type="button"
        class="dashboard-action"
        @click="emit('navigate', item.path)"
      >
        <AppIcon :name="item.icon || 'menu'" :size="18" />
        <span>{{ item.title }}</span>
        <AppIcon name="arrow-right" :size="15" class="dashboard-action__arrow" />
      </button>
    </div>
    <div v-else class="dashboard-actions__empty">暂无可访问入口</div>
  </section>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";

export interface DashboardQuickAction {
  title: string;
  path: string;
  icon?: string;
}

defineProps<{
  items: DashboardQuickAction[];
}>();

const emit = defineEmits<{
  navigate: [path: string];
}>();
</script>
