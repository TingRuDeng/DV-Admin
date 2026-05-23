<template>
  <ul v-if="items.length > 0" class="search-result-list">
    <li
      v-for="(item, index) in items"
      :key="item.path"
      :class="[
        'search-result-list__item',
        {
          'search-result-list__item--active': index === activeIndex,
        },
      ]"
      @click="emit('select', item)"
    >
      <el-icon v-if="item.icon && item.icon.startsWith('el-icon')">
        <component :is="item.icon.replace('el-icon-', '')" />
      </el-icon>
      <div v-else-if="item.icon" :class="`i-svg:${item.icon}`" />
      <div v-else class="i-svg:menu" />
      <span class="ml-2">{{ item.title }}</span>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { SearchItem } from "./types";

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
    display: flex;
    align-items: center;
    padding: 10px;
    text-align: left;
    cursor: pointer;

    &--active {
      color: var(--el-color-primary);
      background-color: var(--el-menu-hover-bg-color);
    }
  }
}
</style>
