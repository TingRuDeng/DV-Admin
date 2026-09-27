<template>
  <el-popover placement="bottom-end" :width="160" trigger="click">
    <template #reference>
      <el-tooltip content="列设置" placement="top">
        <button
          type="button"
          class="ff-column-selector-btn"
          :aria-label="t('table.columnSettings')"
        >
          <AppIcon name="sliders-horizontal" :size="15" />
        </button>
      </el-tooltip>
    </template>
    <div class="ff-column-selector">
      <div class="ff-column-selector__header">
        <span>{{ t("table.columnSettings") }}</span>
        <el-link type="primary" underline="never" @click="emit('reset')">
          {{ t("common.reset") }}
        </el-link>
      </div>
      <el-checkbox-group v-model="innerVisible" class="ff-column-selector__list">
        <el-checkbox
          v-for="col in allColumns"
          :key="col.key"
          :value="col.key"
          :disabled="col.required"
          class="ff-column-selector__item"
        >
          {{ col.label }}
        </el-checkbox>
      </el-checkbox-group>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";

export interface ColumnDef {
  key: string;
  label: string;
  required?: boolean;
}

const props = defineProps<{
  allColumns: ColumnDef[];
  visibleColumns: string[];
}>();

const emit = defineEmits<{
  "update:visibleColumns": [value: string[]];
  reset: [];
}>();

const { t } = useI18n();

const innerVisible = computed({
  get: () => props.visibleColumns,
  set: (val) => emit("update:visibleColumns", val),
});
</script>

<style lang="scss" scoped>
.ff-column-selector-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  color: var(--ff-shell-text-muted);
  cursor: pointer;
  background: transparent;
  border: 1px solid var(--ff-shell-border);
  border-radius: var(--ff-radius-chip);
  transition:
    color var(--ff-duration-fast) ease,
    background-color var(--ff-duration-fast) ease;

  &:hover {
    color: var(--ff-shell-text);
    background: var(--ff-shell-hover);
  }
}

.ff-column-selector {
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--ff-shell-text-muted);
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  &__item {
    width: 100%;
    height: 32px;
    margin: 0;
    font-size: 0.85rem;
  }
}
</style>
