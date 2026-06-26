<template>
  <div class="flex flex-col md:flex-row justify-between gap-y-2.5 mb-2.5">
    <!-- 左侧工具栏 -->
    <div class="toolbar-left flex gap-y-2.5 gap-x-2 md:gap-x-3 flex-wrap">
      <template v-for="(btn, index) in toolbarLeftBtn" :key="index">
        <el-button
          v-hasPerm="btn.perm ?? '*:*:*'"
          v-bind="btn.attrs"
          :disabled="btn.name === 'delete' && disableDelete"
          @click="emit('toolbar', btn.name)"
        >
          {{ btn.text }}
        </el-button>
      </template>
    </div>
    <!-- 右侧工具栏 -->
    <div class="toolbar-right flex gap-y-2.5 gap-x-2 md:gap-x-3 flex-wrap">
      <template v-for="(btn, index) in toolbarRightBtn" :key="index">
        <el-popover v-if="btn.name === 'filter'" placement="bottom" trigger="click">
          <template #reference>
            <el-button v-bind="btn.attrs"></el-button>
          </template>
          <el-scrollbar max-height="350px">
            <template v-for="col in cols" :key="col.prop">
              <el-checkbox
                v-if="col.prop"
                :model-value="col.show"
                :label="col.label"
                @change="emit('columnShowChange', col, Boolean($event))"
              />
            </template>
          </el-scrollbar>
        </el-popover>
        <el-button
          v-else
          v-hasPerm="btn.perm ?? '*:*:*'"
          v-bind="btn.attrs"
          @click="emit('toolbar', btn.name)"
        ></el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { IContentConfig, IObject } from "./types";

type ContentColumn = IContentConfig["cols"][number];

interface ToolbarButton {
  name: string;
  text?: string;
  attrs?: IObject;
  perm?: string | null;
}

defineProps<{
  toolbarLeftBtn: ToolbarButton[];
  toolbarRightBtn: ToolbarButton[];
  cols: ContentColumn[];
  disableDelete: boolean;
}>();

const emit = defineEmits<{
  toolbar: [name: string];
  columnShowChange: [col: ContentColumn, show: boolean];
}>();
</script>

<style lang="scss" scoped>
.toolbar-left,
.toolbar-right {
  .el-button {
    margin-right: 0 !important;
    margin-left: 0 !important;
  }
}
</style>
