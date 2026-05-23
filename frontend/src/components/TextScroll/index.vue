<!--
  TextScroll 组件 - 文本滚动公告
  
  功能：
  - 支持水平方向文本滚动
  - 提供多种预设样式（默认、成功、警告、危险、信息）
  - 支持自定义滚动速度和方向
  - 可选的打字机输入效果
  - 鼠标悬停时暂停滚动
  - 可选的关闭按钮
-->
<template>
  <div
    ref="containerRef"
    class="text-scroll-container"
    :class="[`text-scroll--${props.type}`]"
    :typewriter="props.typewriter ? 'true' : undefined"
  >
    <!-- 左侧图标 -->
    <div class="left-icon">
      <el-icon><Bell /></el-icon>
    </div>
    <!-- 滚动内容包装器 -->
    <div class="scroll-wrapper">
      <div
        ref="scrollContent"
        class="text-scroll-content"
        :class="{ scrolling: shouldScroll }"
        :style="scrollStyle"
      >
        <!-- 滚动内容，复制两份以实现无缝滚动 -->
        <div class="scroll-item" v-html="sanitizedContent" />
        <div class="scroll-item" v-html="sanitizedContent" />
      </div>
    </div>
    <!-- 可选的关闭按钮 -->
    <div v-if="showClose" class="right-icon" @click="handleRightIconClick">
      <el-icon><Close /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TextScrollProps } from "./types";
import { useTextScroll } from "./useTextScroll";

const emit = defineEmits(["close"]);

// 定义组件属性及默认值
const props = withDefaults(defineProps<TextScrollProps>(), {
  speed: 70,
  direction: "left",
  type: "default",
  showClose: false,
  typewriter: false,
  typewriterSpeed: 100,
});

const { containerRef, sanitizedContent, scrollContent, scrollStyle, shouldScroll } =
  useTextScroll(props);

/**
 * 处理关闭按钮点击事件
 * 触发 close 事件，并直接销毁当前组件
 */
const handleRightIconClick = () => {
  emit("close");
  // 获取当前组件的DOM元素
  if (containerRef.value) {
    // 从DOM中移除元素
    containerRef.value.remove();
  }
};
</script>

<style scoped lang="scss">
.text-scroll-container {
  position: relative;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  width: 100%;
  padding-right: 16px;
  overflow: hidden;
  background-color: var(--el-color-primary-light-9) !important;
  border: 1px solid var(--main-color);
  border-radius: calc(var(--custom-radius) / 2 + 2px) !important;

  .left-icon,
  .right-icon {
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 100%;
    text-align: center;
    background-color: var(--el-color-primary-light-9) !important;
  }

  .left-icon {
    left: 0;
  }

  .right-icon {
    right: 0;
    cursor: pointer;
    background-color: transparent !important;
  }

  .scroll-wrapper {
    flex: 1;
    margin-left: 34px;
    overflow: hidden;
  }

  .text-scroll-content {
    display: flex;
    height: 34px;
    line-height: 34px;
    white-space: nowrap;
    animation: scroll linear infinite;
    animation-duration: var(--animation-duration);
    animation-direction: var(--animation-direction);
    animation-play-state: var(--animation-play-state);

    .scroll-item {
      display: inline-block;
      min-width: 100%;
      padding: 0 10px;
      font-size: 14px;
      color: var(--el-color-primary-light-2) !important;
      text-align: left;
      text-align: center;

      :deep(a) {
        color: #fd4e4e !important;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  @keyframes scroll {
    0% {
      transform: translateX(0);
    }

    100% {
      transform: translateX(-100%);
    }
  }

  // 添加类型样式
  &.text-scroll--default {
    background-color: var(--el-color-primary-light-9) !important;
    border-color: var(--el-color-primary);

    .right-icon,
    .left-icon i {
      color: var(--el-color-primary) !important;
    }

    .scroll-item {
      color: var(--el-color-primary) !important;
    }
  }

  &.text-scroll--success {
    background-color: var(--el-color-success-light-9) !important;
    border-color: var(--el-color-success);

    .left-icon {
      background-color: var(--el-color-success-light-9) !important;

      i {
        color: var(--el-color-success);
      }
    }

    .scroll-item {
      color: var(--el-color-success) !important;
    }
  }

  &.text-scroll--warning {
    background-color: var(--el-color-warning-light-9) !important;
    border-color: var(--el-color-warning);

    .left-icon {
      background-color: var(--el-color-warning-light-9) !important;

      i {
        color: var(--el-color-warning);
      }
    }

    .scroll-item {
      color: var(--el-color-warning) !important;
    }
  }

  &.text-scroll--danger {
    background-color: var(--el-color-danger-light-9) !important;
    border-color: var(--el-color-danger);

    .left-icon {
      background-color: var(--el-color-danger-light-9) !important;

      i {
        color: var(--el-color-danger);
      }
    }

    .scroll-item {
      color: var(--el-color-danger) !important;
    }
  }

  &.text-scroll--info {
    background-color: var(--el-color-info-light-9) !important;
    border-color: var(--el-color-info);

    .left-icon {
      background-color: var(--el-color-info-light-9) !important;

      i {
        color: var(--el-color-info);
      }
    }

    .scroll-item {
      color: var(--el-color-info) !important;
    }
  }
}

// 添加打字机效果的光标样式
.text-scroll-content .scroll-item {
  &::after {
    content: "";
    opacity: 0;
    animation: none;
  }
}

// 仅在启用打字机效果时显示光标
.text-scroll-container[typewriter] .text-scroll-content .scroll-item::after {
  content: "|";
  opacity: 0;
  animation: cursor 1s infinite;
}

@keyframes cursor {
  0%,
  100% {
    opacity: 0;
  }

  50% {
    opacity: 1;
  }
}
</style>
