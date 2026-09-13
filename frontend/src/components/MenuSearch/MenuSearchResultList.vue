<template>
  <ul v-if="items.length > 0" class="search-result-list">
    <li
      v-for="(item, index) in items"
      :key="item.path"
      :data-active="index === activeIndex"
      :class="[
        'search-result-list__item',
        {
          'search-result-list__item--active': index === activeIndex,
        },
      ]"
    >
      <button type="button" @click="emit('select', item)">
        <AppIcon :name="normalizeAppIconName(item.icon || 'menu')" :size="16" />
        <span class="ml-2">{{ item.title }}</span>
      </button>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { SearchItem } from "./types";
import AppIcon from "@/components/AppIcon/index.vue";
import { normalizeAppIconName } from "@/components/AppIcon/icon-map";

defineProps<{
  activeIndex: number;
  items: SearchItem[];
}>();

const emit = defineEmits<{
  select: [item: SearchItem];
}>();
</script>

<style scoped lang="scss">
.search-result-list {
  padding: 0;
  margin: 0;
  list-style: none;

  &__item {
    button {
      display: flex;
      align-items: center;
      width: 100%;
      padding: 10px;
      color: inherit;
      text-align: left;
      cursor: pointer;
      background: transparent;
      border: 0;

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: -2px;
      }
    }

    &--active {
      color: var(--el-color-primary);
      background-color: var(--el-menu-hover-bg-color);
    }
  }
}
</style>
