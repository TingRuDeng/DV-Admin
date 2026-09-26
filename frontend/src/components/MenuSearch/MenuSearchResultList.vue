<template>
  <!-- 只渲染 option，外层 listbox 由 index.vue 提供 -->
  <li
    v-for="(item, index) in items"
    :id="`${idPrefix}-${index}`"
    :key="item.path"
    role="option"
    :aria-selected="index === activeIndex"
    :class="['menu-search__option', { 'is-active': index === activeIndex }]"
    @click="emit('select', item)"
  >
    <AppIcon :name="normalizeMenuIconName(item.icon)" :size="16" class="menu-search__option-icon" />
    <span class="menu-search__option-label">{{ item.title }}</span>
  </li>
</template>

<script setup lang="ts">
import type { SearchItem } from "./types";
import AppIcon from "@/components/AppIcon/index.vue";
import { normalizeMenuIconName } from "@/components/AppIcon/icon-map";

defineProps<{
  activeIndex: number;
  idPrefix: string;
  items: SearchItem[];
}>();

const emit = defineEmits<{
  select: [item: SearchItem];
}>();
</script>
