<template>
  <Teleport to="body">
    <ul
      v-show="visible"
      class="contextmenu"
      role="menu"
      aria-label="标签页操作"
      :style="{ left: x + 'px', top: y + 'px' }"
    >
      <li role="none">
        <button type="button" role="menuitem" @click="emit('refresh')">
          <div class="i-svg:refresh" aria-hidden="true" />
          刷新
        </button>
      </li>
      <li v-if="!selectedTag?.affix" role="none">
        <button type="button" role="menuitem" @click="emit('close')">
          <div class="i-svg:close" aria-hidden="true" />
          关闭
        </button>
      </li>
      <li role="none">
        <button type="button" role="menuitem" @click="emit('close-other')">
          <div class="i-svg:close_other" aria-hidden="true" />
          关闭其它
        </button>
      </li>
      <li v-if="!isFirstView" role="none">
        <button type="button" role="menuitem" @click="emit('close-left')">
          <div class="i-svg:close_left" aria-hidden="true" />
          关闭左侧
        </button>
      </li>
      <li v-if="!isLastView" role="none">
        <button type="button" role="menuitem" @click="emit('close-right')">
          <div class="i-svg:close_right" aria-hidden="true" />
          关闭右侧
        </button>
      </li>
      <li role="none">
        <button type="button" role="menuitem" @click="emit('close-all')">
          <div class="i-svg:close_all" aria-hidden="true" />
          关闭所有
        </button>
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
  color: var(--ff-shell-text);
  list-style-type: none;
  background: var(--ff-shell-surface);
  border: 1px solid var(--ff-shell-border);
  border-radius: var(--ff-radius-shell);
  box-shadow: var(--ff-shadow-shell-raised);

  li button {
    display: flex;
    gap: 10px;
    align-items: center;
    width: 100%;
    padding: 10px 16px;
    margin: 0;
    font: inherit;
    color: inherit;
    text-align: left;
    cursor: pointer;
    background: transparent;
    border: 0;
    transition:
      color var(--ff-duration-fast) ease,
      background-color var(--ff-duration-fast) ease;

    &:hover,
    &:focus-visible {
      color: var(--el-color-primary);
      outline: none;
      background: var(--ff-shell-hover);
    }
  }

  li:first-child button {
    border-radius: var(--ff-radius-shell) var(--ff-radius-shell) 0 0;
  }

  li:last-child button {
    border-radius: 0 0 var(--ff-radius-shell) var(--ff-radius-shell);
  }
}
</style>
