<template>
  <div class="search-history">
    <div class="search-history__title">
      {{ t("menuSearch.history") }}
      <el-button
        type="primary"
        text
        size="small"
        class="search-history__clear"
        :aria-label="t('menuSearch.clearHistory')"
        :title="t('menuSearch.clearHistory')"
        @click="emit('clear')"
      >
        <AppIcon name="trash" :size="15" />
      </el-button>
    </div>
    <ul class="search-history__list">
      <li
        v-for="(item, index) in items"
        :key="item.path"
        class="search-history__item"
        :data-active="index === activeIndex"
      >
        <button type="button" class="search-history__navigate" @click="emit('select', item)">
          <span class="search-history__icon">
            <AppIcon name="activity" :size="15" />
          </span>
          <span class="search-history__name">{{ item.title }}</span>
        </button>
        <div class="search-history__action">
          <button
            type="button"
            :aria-label="t('menuSearch.removeHistory')"
            :title="t('menuSearch.removeHistory')"
            @click.stop="emit('remove', index)"
          >
            <AppIcon name="close" :size="15" />
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { SearchItem } from "./types";
import AppIcon from "@/components/AppIcon/index.vue";

defineProps<{
  items: SearchItem[];
  activeIndex?: number;
}>();

const emit = defineEmits<{
  clear: [];
  remove: [index: number];
  select: [item: SearchItem];
}>();

const { t } = useI18n();
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

  &__navigate {
    display: flex;
    flex: 1;
    align-items: center;
    min-width: 0;
    height: 100%;
    padding: 0;
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

    button {
      display: inline-flex;
      padding: 0;
      color: inherit;
      cursor: pointer;
      background: transparent;
      border: 0;
    }

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

    &:hover,
    &:focus-within,
    &[data-active="true"] {
      background-color: var(--el-fill-color-light);

      .search-history__action {
        opacity: 1;
      }
    }
  }
}
</style>
