<template>
  <!-- 只渲染 option，外层 listbox 和清空按钮由 index.vue 提供 -->
  <li
    v-for="(item, index) in items"
    :id="`${idPrefix}-${index}`"
    :key="item.path"
    role="option"
    :aria-selected="index === activeIndex"
    :class="['menu-search__option', { 'is-active': index === activeIndex }]"
    @click="emit('select', item)"
  >
    <AppIcon name="activity" :size="16" class="menu-search__option-icon" />
    <span class="menu-search__option-label">{{ item.title }}</span>
    <!-- option 内不能放可聚焦控件：删除只给鼠标用，键盘用户按 Delete 删除高亮项 -->
    <span class="menu-search__remove" aria-hidden="true" @click.stop="emit('remove', index)">
      <AppIcon name="close" :size="14" />
    </span>
  </li>
</template>

<script setup lang="ts">
import type { SearchItem } from "./types";
import AppIcon from "@/components/AppIcon/index.vue";

defineProps<{
  activeIndex: number;
  idPrefix: string;
  items: SearchItem[];
}>();

const emit = defineEmits<{
  remove: [index: number];
  select: [item: SearchItem];
}>();
</script>
