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
              <div
                v-if="item.value === LayoutMode.TOP || item.value === LayoutMode.MIX"
                class="layout-header"
              ></div>
              <div v-if="item.value !== LayoutMode.TOP" class="layout-sidebar"></div>
              <div v-if="item.value === LayoutMode.DOUBLE" class="layout-panel"></div>
              <div class="layout-main"></div>
            </div>
            <div class="layout-name">{{ item.label }}</div>
            <div v-if="settingsStore.layout === item.value" class="layout-check">
              <AppIcon name="check" :size="12" />
            </div>
          </div>
        </el-tooltip>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { LayoutMode } from "@/enums";
import { useSettingsStore } from "@/store";
import type { LayoutOption } from "./types";
import AppIcon from "@/components/AppIcon/index.vue";

const { t } = useI18n();
const settingsStore = useSettingsStore();

const layoutOptions: LayoutOption[] = [
  { value: LayoutMode.LEFT, label: t("settings.leftLayout"), className: "left" },
  { value: LayoutMode.TOP, label: t("settings.topLayout"), className: "top" },
  { value: LayoutMode.MIX, label: t("settings.mixLayout"), className: "mix" },
  { value: LayoutMode.DOUBLE, label: t("settings.doubleLayout"), className: "double" },
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
    // 四种布局放一行：抽屉内容区约 290px 宽，每个预览 62px、间距 8px
    grid-template-columns: repeat(4, 62px);
    gap: 8px;
    justify-content: center;
  }
}

.layout-item {
  position: relative;
  width: 62px;
  height: 80px;
  overflow: hidden;
  cursor: pointer;
  background: var(--ff-field-bg);
  border: 2px solid var(--ff-line);
  border-radius: 14px;
  transition:
    background-color var(--ff-duration-fast) ease,
    border-color var(--ff-duration-fast) ease;

  &:hover {
    background: var(--ff-hover);
    border-color: color-mix(in srgb, var(--ff-iri-b) 40%, transparent);
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
    background: var(--ff-iri);
    border-radius: 2px;
  }

  .layout-sidebar {
    position: absolute;
    left: 4px;
    width: 12px;
    background: linear-gradient(180deg, var(--ff-iri-a) 0%, var(--ff-iri-b) 100%);
    border-radius: 2px;
  }

  .layout-panel {
    position: absolute;
    left: 14px;
    width: 12px;
    background: color-mix(in srgb, var(--ff-iri-b) 35%, transparent);
    border-radius: 2px;
  }

  .layout-main {
    position: absolute;
    background: linear-gradient(135deg, var(--ff-hover) 0%, var(--ff-press) 100%);
    border: 1px solid var(--ff-line);
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
    transition: color var(--ff-duration-fast) ease;
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
    color: var(--ff-on-iri);
    background: var(--ff-iri);
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

  &.double {
    .layout-sidebar {
      top: 4px;
      bottom: 4px;
      width: 8px;
    }

    .layout-panel {
      top: 4px;
      bottom: 4px;
    }

    .layout-main {
      top: 4px;
      right: 4px;
      bottom: 4px;
      left: 30px;
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

  // 当前布局：面板底色 + 虹彩描边
  &.is-active {
    background:
      linear-gradient(var(--ff-color-bg-panel-strong), var(--ff-color-bg-panel-strong)) padding-box,
      var(--ff-iri) border-box;
    border-color: transparent;

    .layout-name {
      font-weight: 600;
      color: var(--ff-accent);
    }
  }
}
</style>
