<template>
  <div class="search-history">
    <div class="search-history__title">
      搜索历史
      <el-button
        type="primary"
        text
        size="small"
        class="search-history__clear"
        @click="emit('clear')"
      >
        <el-icon><Delete /></el-icon>
      </el-button>
    </div>
    <ul class="search-history__list">
      <li
        v-for="(item, index) in items"
        :key="index"
        class="search-history__item"
        @click="emit('select', item)"
      >
        <div class="search-history__icon">
          <el-icon><Clock /></el-icon>
        </div>
        <span class="search-history__name">{{ item.title }}</span>
        <div class="search-history__action">
          <el-icon @click.stop="emit('remove', index)"><Close /></el-icon>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { Clock, Close, Delete } from "@element-plus/icons-vue";
import type { SearchItem } from "./types";

defineProps<{
  items: SearchItem[];
}>();

const emit = defineEmits<{
  clear: [];
  remove: [index: number];
  select: [item: SearchItem];
}>();
</script>

<style scoped lang="scss">
.search-history {
  &__title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    font-size: 12px;
    line-height: 34px;
    color: var(--el-text-color-secondary);
  }

  &__clear {
    padding: 2px;
    font-size: 12px;

    &:hover {
      color: var(--el-color-danger);
    }
  }

  &__list {
    padding: 0;
    margin: 0;
  }

  &__icon {
    display: flex;
    align-items: center;
    margin-right: 10px;
    font-size: 16px;
    color: var(--el-text-color-secondary);
  }

  &__name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 14px;
    color: var(--el-text-color-primary);
    white-space: nowrap;
  }

  &__action {
    padding: 4px;
    color: var(--el-text-color-secondary);
    border-radius: 4px;
    opacity: 0;
    transition: opacity 0.2s;

    &:hover {
      color: var(--el-color-danger);
      background-color: var(--el-fill-color);
    }
  }

  &__item {
    display: flex;
    align-items: center;
    height: 40px;
    padding: 0 12px;
    cursor: pointer;

    &:hover {
      background-color: var(--el-fill-color-light);

      .search-history__action {
        opacity: 1;
      }
    }
  }
}
</style>
