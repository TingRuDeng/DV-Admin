<template>
  <section class="dashboard-actions" aria-labelledby="dashboard-actions-title">
    <h2 id="dashboard-actions-title" class="dashboard-actions__title">快捷入口</h2>

    <div v-if="items.length" class="dashboard-actions__grid">
      <button
        v-for="(item, index) in items"
        :key="item.path"
        type="button"
        class="dashboard-action"
        :style="{ '--i': index }"
        @click="emit('navigate', item.path)"
      >
        <AppIcon :name="item.icon || 'menu'" :size="22" :stroke-width="1.4" />
        <span class="dashboard-action__title">{{ item.title }}</span>
        <AppIcon name="arrow-up-right" :size="16" class="dashboard-action__arrow" />
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
