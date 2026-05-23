<template>
  <Teleport to="body">
    <ul v-show="visible" class="contextmenu" :style="{ left: x + 'px', top: y + 'px' }">
      <li @click="emit('refresh')">
        <div class="i-svg:refresh" />
        刷新
      </li>
      <li v-if="!selectedTag?.affix" @click="emit('close')">
        <div class="i-svg:close" />
        关闭
      </li>
      <li @click="emit('close-other')">
        <div class="i-svg:close_other" />
        关闭其它
      </li>
      <li v-if="!isFirstView" @click="emit('close-left')">
        <div class="i-svg:close_left" />
        关闭左侧
      </li>
      <li v-if="!isLastView" @click="emit('close-right')">
        <div class="i-svg:close_right" />
        关闭右侧
      </li>
      <li @click="emit('close-all')">
        <div class="i-svg:close_all" />
        关闭所有
      </li>
    </ul>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  isFirstView: boolean;
  isLastView: boolean;
  selectedTag: TagView | null;
  visible: boolean;
  x: number;
  y: number;
}>();

const emit = defineEmits<{
  close: [];
  "close-all": [];
  "close-left": [];
  "close-other": [];
  "close-right": [];
  refresh: [];
}>();
</script>

<style lang="scss" scoped>
.contextmenu {
  position: absolute;
  z-index: 3000;
  padding: 8px 0;
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  list-style-type: none;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);

  li {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 10px 16px;
    margin: 0;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      color: #3b82f6;
      background: rgba(59, 130, 246, 0.08);
    }

    &:first-child {
      border-radius: 12px 12px 0 0;
    }

    &:last-child {
      border-radius: 0 0 12px 12px;
    }
  }
}

:global(html.dark) {
  .contextmenu {
    color: #e2e8f0;
    background: rgba(30, 41, 59, 0.95);
    border-color: rgba(255, 255, 255, 0.08);

    li:hover {
      color: #60a5fa;
      background: rgba(96, 165, 250, 0.15);
    }
  }
}
</style>
