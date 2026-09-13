<template>
  <section class="dashboard-actions" aria-labelledby="dashboard-actions-title">
    <div class="dashboard-actions__header">
      <div>
        <h2 id="dashboard-actions-title">{{ t("dashboard.quickActions") }}</h2>
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
    <div v-else class="dashboard-actions__empty">{{ t("dashboard.empty") }}</div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import AppIcon from "@/components/AppIcon/index.vue";

const { t } = useI18n();

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
