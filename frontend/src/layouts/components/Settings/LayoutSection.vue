<template>
  <section class="config-section">
    <el-divider>{{ t("settings.navigation") }}</el-divider>

    <div class="layout-select">
      <div class="layout-grid">
        <el-tooltip
          v-for="item in layoutOptions"
          :key="item.value"
          :content="item.label"
          placement="bottom"
        >
          <div
            role="button"
            tabindex="0"
            :class="[
              'layout-item',
              item.className,
              {
                'is-active': settingsStore.layout === item.value,
              },
            ]"
            @click="handleLayoutChange(item.value)"
            @keydown.enter.space="handleLayoutChange(item.value)"
          >
            <div class="layout-preview">
              <div v-if="item.value !== LayoutMode.LEFT" class="layout-header"></div>
              <div v-if="item.value !== LayoutMode.TOP" class="layout-sidebar"></div>
              <div class="layout-main"></div>
            </div>
            <div class="layout-name">{{ item.label }}</div>
            <div v-if="settingsStore.layout === item.value" class="layout-check">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </el-tooltip>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Check } from "@element-plus/icons-vue";
import { LayoutMode } from "@/enums";
import { useSettingsStore } from "@/store";
import type { LayoutOption } from "./types";

const { t } = useI18n();
const settingsStore = useSettingsStore();

const layoutOptions: LayoutOption[] = [
  { value: LayoutMode.LEFT, label: t("settings.leftLayout"), className: "left" },
  { value: LayoutMode.TOP, label: t("settings.topLayout"), className: "top" },
  { value: LayoutMode.MIX, label: t("settings.mixLayout"), className: "mix" },
];

function handleLayoutChange(layout: LayoutMode) {
  if (settingsStore.layout === layout) return;

  settingsStore.updateLayout(layout);
}
</script>

<style lang="scss" scoped>
.config-section {
  margin-bottom: 24px;
}

.layout-select {
  padding: 16px 8px;

  .layout-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    justify-items: center;
  }
}

.layout-item {
  position: relative;
  width: 70px;
  height: 80px;
  overflow: hidden;
  cursor: pointer;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid var(--el-border-color-light);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: linear-gradient(145deg, #ffffff 0%, var(--el-color-primary-light-9) 100%);
    border-color: var(--el-color-primary-light-3);
    transform: translateY(-4px) scale(1.05);
  }

  &:active {
    transform: translateY(-2px) scale(1.02);
  }

  .layout-preview {
    position: relative;
    width: 100%;
    height: 50px;
    margin: 8px 0 4px 0;
  }

  .layout-header {
    position: absolute;
    top: 0;
    right: 4px;
    left: 4px;
    height: 8px;
    background: linear-gradient(
      90deg,
      var(--el-color-primary) 0%,
      var(--el-color-primary-light-3) 100%
    );
    border-radius: 2px;
  }

  .layout-sidebar {
    position: absolute;
    left: 4px;
    width: 12px;
    background: linear-gradient(
      180deg,
      var(--el-color-primary-dark-2) 0%,
      var(--el-color-primary) 100%
    );
    border-radius: 2px;
  }

  .layout-main {
    position: absolute;
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 2px;
  }

  .layout-name {
    position: absolute;
    right: 0;
    bottom: 6px;
    left: 0;
    font-size: 10px;
    font-weight: 500;
    color: var(--el-text-color-regular);
    text-align: center;
    transition: color 0.3s ease;
  }

  .layout-check {
    position: absolute;
    top: 4px;
    right: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    font-size: 10px;
    color: white;
    background: var(--el-color-success);
    border-radius: 50%;
  }

  &.left {
    .layout-sidebar {
      top: 4px;
      bottom: 4px;
    }

    .layout-main {
      top: 4px;
      right: 4px;
      bottom: 4px;
      left: 20px;
    }
  }

  &.top {
    .layout-header {
      height: 12px;
    }

    .layout-main {
      top: 16px;
      right: 4px;
      bottom: 4px;
      left: 4px;
    }
  }

  &.mix {
    .layout-header {
      height: 10px;
    }

    .layout-sidebar {
      top: 14px;
      bottom: 4px;
    }

    .layout-main {
      top: 14px;
      right: 4px;
      bottom: 4px;
      left: 20px;
    }
  }

  &.is-active {
    background: linear-gradient(
      145deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-color-primary-light-8) 100%
    );
    border-color: var(--el-color-primary);
    transform: translateY(-2px) scale(1.08);

    .layout-name {
      font-weight: 600;
      color: var(--el-color-primary);
    }
  }
}

:global(.dark) {
  .layout-item {
    background: linear-gradient(145deg, var(--el-bg-color) 0%, var(--el-bg-color-page) 100%);
    border-color: var(--el-border-color);

    &:hover {
      background: linear-gradient(
        145deg,
        var(--el-bg-color-page) 0%,
        var(--el-color-primary-light-9) 100%
      );
    }

    &.is-active {
      background: linear-gradient(
        145deg,
        var(--el-color-primary-light-9) 0%,
        var(--el-color-primary-light-8) 100%
      );
    }

    .layout-main {
      background: linear-gradient(135deg, var(--el-fill-color) 0%, var(--el-fill-color-light) 100%);
    }
  }
}
</style>
