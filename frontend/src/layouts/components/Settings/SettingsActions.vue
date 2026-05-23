<template>
  <div class="action-buttons">
    <el-tooltip
      content="复制配置将生成当前设置的代码，覆盖 src/settings.ts 下的 defaultSettings 变量"
      placement="top"
    >
      <el-button
        type="primary"
        size="default"
        :icon="copyIcon"
        :loading="copyLoading"
        @click="emit('copy')"
      >
        {{ copyLoading ? "复制中..." : t("settings.copyConfig") }}
      </el-button>
    </el-tooltip>
    <el-tooltip content="重置将恢复所有设置为默认值" placement="top">
      <el-button
        type="warning"
        size="default"
        :icon="resetIcon"
        :loading="resetLoading"
        @click="emit('reset')"
      >
        {{ resetLoading ? "重置中..." : t("settings.resetConfig") }}
      </el-button>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { DocumentCopy, RefreshLeft } from "@element-plus/icons-vue";

defineProps<{
  copyLoading: boolean;
  resetLoading: boolean;
}>();

const emit = defineEmits<{
  copy: [];
  reset: [];
}>();

const { t } = useI18n();

const copyIcon = markRaw(DocumentCopy);
const resetIcon = markRaw(RefreshLeft);
</script>

<style lang="scss" scoped>
.action-buttons {
  display: flex;

  & > .el-button {
    flex: 1;
    font-size: 14px;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transform: translateY(-2px);
    }
  }
}
</style>
