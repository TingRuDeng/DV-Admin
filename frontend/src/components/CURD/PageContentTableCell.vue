<template>
  <!-- 显示图片 -->
  <template v-if="col.templet === 'image'">
    <template v-if="col.prop">
      <template v-if="Array.isArray(row[col.prop])">
        <template v-for="(item, index) in toImageList(row[col.prop])" :key="item">
          <el-image
            :src="item"
            :preview-src-list="toImageList(row[col.prop])"
            :initial-index="index"
            :preview-teleported="true"
            :style="`width: ${col.imageWidth ?? 40}px; height: ${col.imageHeight ?? 40}px`"
          />
        </template>
      </template>
      <template v-else>
        <el-image
          :src="toDisplayText(row[col.prop])"
          :preview-src-list="toImageList(row[col.prop])"
          :preview-teleported="true"
          :style="`width: ${col.imageWidth ?? 40}px; height: ${col.imageHeight ?? 40}px`"
        />
      </template>
    </template>
  </template>
  <!-- 根据行的selectList属性返回对应列表值 -->
  <template v-else-if="col.templet === 'list'">
    <template v-if="col.prop">
      {{ getSelectLabel(col.selectList, row[col.prop]) }}
    </template>
  </template>
  <!-- 格式化显示链接 -->
  <template v-else-if="col.templet === 'url'">
    <template v-if="col.prop">
      <el-link type="primary" :href="toDisplayText(row[col.prop])" target="_blank">
        {{ toDisplayText(row[col.prop]) }}
      </el-link>
    </template>
  </template>
  <!-- 生成开关组件 -->
  <template v-else-if="col.templet === 'switch'">
    <template v-if="col.prop">
      <!-- pageDataLength>0: 解决el-switch组件会在表格初始化的时候触发一次change事件 -->
      <el-switch
        :model-value="toEditableValue(row[col.prop])"
        :active-value="col.activeValue ?? 1"
        :inactive-value="col.inactiveValue ?? 0"
        :inline-prompt="true"
        :active-text="col.activeText ?? ''"
        :inactive-text="col.inactiveText ?? ''"
        :validate-event="false"
        :disabled="!hasButtonPerm(col.prop)"
        @update:model-value="setRowValue(row, col.prop, $event)"
        @change="
          pageDataLength > 0 && emit('modify', col.prop, toEditableValue(row[col.prop]), row)
        "
      />
    </template>
  </template>
  <!-- 生成输入框组件 -->
  <template v-else-if="col.templet === 'input'">
    <template v-if="col.prop">
      <el-input
        :model-value="toDisplayText(row[col.prop])"
        :type="col.inputType ?? 'text'"
        :disabled="!hasButtonPerm(col.prop)"
        @update:model-value="setRowValue(row, col.prop, $event)"
        @blur="emit('modify', col.prop, toEditableValue(row[col.prop]), row)"
      />
    </template>
  </template>
  <!-- 格式化为价格 -->
  <template v-else-if="col.templet === 'price'">
    <template v-if="col.prop">
      {{ `${col.priceFormat ?? "￥"}${row[col.prop]}` }}
    </template>
  </template>
  <!-- 格式化为百分比 -->
  <template v-else-if="col.templet === 'percent'">
    <template v-if="col.prop">{{ row[col.prop] }}%</template>
  </template>
  <!-- 显示图标 -->
  <template v-else-if="col.templet === 'icon'">
    <template v-if="col.prop">
      <template v-if="toDisplayText(row[col.prop]).startsWith('el-icon-')">
        <el-icon>
          <component :is="toDisplayText(row[col.prop]).replace('el-icon-', '')" />
        </el-icon>
      </template>
      <template v-else>
        <div class="i-svg:{{ row[col.prop] }}" />
      </template>
    </template>
  </template>
  <!-- 格式化时间 -->
  <template v-else-if="col.templet === 'date'">
    <template v-if="col.prop">
      {{ formatDateValue(row[col.prop], col.dateFormat ?? "YYYY-MM-DD HH:mm:ss") }}
    </template>
  </template>
  <!-- 列操作栏 -->
  <template v-else-if="col.templet === 'tool'">
    <template v-for="(btn, index) in tableToolbarBtn" :key="index">
      <el-button
        v-if="btn.render === undefined || btn.render(row)"
        v-hasPerm="btn.perm ?? '*:*:*'"
        v-bind="btn.attrs"
        @click="
          emit('operate', {
            name: btn.name,
            row,
            column,
            $index: rowIndex,
          })
        "
      >
        {{ btn.text }}
      </el-button>
    </template>
  </template>
</template>

<script setup lang="ts">
import { useDateFormat } from "@vueuse/core";
import type { IContentConfig, IObject, IOperateData } from "./types";
import type { PageContentToolbarButton } from "./usePageContentToolbarConfig";

type PageContentColumn = IContentConfig["cols"][number];
type SelectKey = string | number;

defineProps<{
  col: PageContentColumn;
  row: IObject;
  column: IObject;
  rowIndex: number;
  pageDataLength: number;
  tableToolbarBtn: PageContentToolbarButton[];
  hasButtonPerm: (action: string) => boolean;
}>();

const emit = defineEmits<{
  modify: [field: string, value: boolean | string | number, row: IObject];
  operate: [data: IOperateData];
}>();

// 将动态行值转成 Element Plus 可接收的展示文本。
function toDisplayText(value: unknown) {
  return value == null ? "" : String(value);
}

// 图片模板历史上支持单值和数组，这里统一收敛为预览列表。
function toImageList(value: unknown) {
  const values = Array.isArray(value) ? value : [value];
  return values.map(toDisplayText).filter(Boolean);
}

// 行内编辑只向修改接口提交基础标量，复杂值按原展示语义转文本。
function toEditableValue(value: unknown): boolean | string | number {
  if (typeof value === "boolean" || typeof value === "number" || typeof value === "string") {
    return value;
  }
  return toDisplayText(value);
}

// 列表映射只能使用字符串或数字键，复杂值沿用文本化查找。
function toSelectKey(value: unknown): SelectKey {
  return typeof value === "string" || typeof value === "number" ? value : toDisplayText(value);
}

// 从列配置的 selectList 中读取展示标签，缺失时保持空文本。
function getSelectLabel(selectList: IObject | undefined, value: unknown) {
  return (selectList ?? {})[toSelectKey(value)] ?? "";
}

// 日期模板只负责展示，把动态行值转成 VueUse 可格式化的输入。
function formatDateValue(value: unknown, format: string) {
  if (!value) {
    return "";
  }
  return useDateFormat(toDisplayText(value), format).value;
}

// 替代模板中的动态 v-model，避免通用对象值从 unknown 逃逸。
function setRowValue(row: IObject, prop: string, value: unknown) {
  row[prop] = value;
}
</script>
