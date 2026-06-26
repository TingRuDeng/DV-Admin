<template>
  <!-- 显示图片 -->
  <template v-if="col.templet === 'image'">
    <template v-if="col.prop">
      <template v-if="Array.isArray(row[col.prop])">
        <template v-for="(item, index) in row[col.prop]" :key="item">
          <el-image
            :src="item"
            :preview-src-list="row[col.prop]"
            :initial-index="index"
            :preview-teleported="true"
            :style="`width: ${col.imageWidth ?? 40}px; height: ${col.imageHeight ?? 40}px`"
          />
        </template>
      </template>
      <template v-else>
        <el-image
          :src="row[col.prop]"
          :preview-src-list="[row[col.prop]]"
          :preview-teleported="true"
          :style="`width: ${col.imageWidth ?? 40}px; height: ${col.imageHeight ?? 40}px`"
        />
      </template>
    </template>
  </template>
  <!-- 根据行的selectList属性返回对应列表值 -->
  <template v-else-if="col.templet === 'list'">
    <template v-if="col.prop">
      {{ (col.selectList ?? {})[row[col.prop]] }}
    </template>
  </template>
  <!-- 格式化显示链接 -->
  <template v-else-if="col.templet === 'url'">
    <template v-if="col.prop">
      <el-link type="primary" :href="row[col.prop]" target="_blank">
        {{ row[col.prop] }}
      </el-link>
    </template>
  </template>
  <!-- 生成开关组件 -->
  <template v-else-if="col.templet === 'switch'">
    <template v-if="col.prop">
      <!-- pageDataLength>0: 解决el-switch组件会在表格初始化的时候触发一次change事件 -->
      <el-switch
        v-model="row[col.prop]"
        :active-value="col.activeValue ?? 1"
        :inactive-value="col.inactiveValue ?? 0"
        :inline-prompt="true"
        :active-text="col.activeText ?? ''"
        :inactive-text="col.inactiveText ?? ''"
        :validate-event="false"
        :disabled="!hasButtonPerm(col.prop)"
        @change="pageDataLength > 0 && emit('modify', col.prop, row[col.prop], row)"
      />
    </template>
  </template>
  <!-- 生成输入框组件 -->
  <template v-else-if="col.templet === 'input'">
    <template v-if="col.prop">
      <el-input
        v-model="row[col.prop]"
        :type="col.inputType ?? 'text'"
        :disabled="!hasButtonPerm(col.prop)"
        @blur="emit('modify', col.prop, row[col.prop], row)"
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
      <template v-if="row[col.prop].startsWith('el-icon-')">
        <el-icon>
          <component :is="row[col.prop].replace('el-icon-', '')" />
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
      {{
        row[col.prop]
          ? useDateFormat(row[col.prop], col.dateFormat ?? "YYYY-MM-DD HH:mm:ss").value
          : ""
      }}
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
import type { ButtonProps } from "element-plus";
import type { CSSProperties } from "vue";
import type { IContentConfig, IObject, IOperateData } from "./types";

type PageContentColumn = IContentConfig["cols"][number];

export interface PageContentTableButton {
  name: string;
  text?: string;
  perm?: string | null;
  attrs?: Partial<ButtonProps> & { style?: CSSProperties };
  render?: (row: IObject) => boolean;
}

defineProps<{
  col: PageContentColumn;
  row: IObject;
  column: IObject;
  rowIndex: number;
  pageDataLength: number;
  tableToolbarBtn: PageContentTableButton[];
  hasButtonPerm: (action: string) => boolean;
}>();

const emit = defineEmits<{
  modify: [field: string, value: boolean | string | number, row: IObject];
  operate: [data: IOperateData];
}>();
</script>
