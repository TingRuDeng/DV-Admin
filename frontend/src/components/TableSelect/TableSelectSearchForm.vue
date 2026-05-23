<template>
  <el-form ref="formRef" :model="queryParams" :inline="true">
    <template v-for="item in formItems" :key="item.prop">
      <el-form-item :label="item.label" :prop="item.prop">
        <el-input
          v-if="isInputItem(item)"
          :model-value="getInputValue(item.prop)"
          v-bind="item.attrs"
          @update:model-value="setFieldValue(item.prop, $event)"
          @keyup.enter="emit('query')"
        />
        <el-input
          v-else-if="isNumberInputItem(item)"
          :model-value="getInputValue(item.prop)"
          v-bind="item.attrs"
          @update:model-value="setFieldValue(item.prop, $event)"
          @keyup.enter="emit('query')"
        />
        <el-select
          v-else-if="item.type === 'select'"
          :model-value="getSelectValue(item.prop)"
          v-bind="item.attrs"
          @update:model-value="setFieldValue(item.prop, $event)"
        >
          <template v-for="option in item.options" :key="String(option.value)">
            <el-option :label="option.label" :value="getOptionValue(option.value)" />
          </template>
        </el-select>
        <el-tree-select
          v-else-if="item.type === 'tree-select'"
          :model-value="getTreeSelectValue(item.prop)"
          v-bind="item.attrs"
          @update:model-value="setFieldValue(item.prop, $event)"
        />
        <el-date-picker
          v-else-if="item.type === 'date-picker'"
          :model-value="getDatePickerValue(item.prop)"
          v-bind="item.attrs"
          @update:model-value="setFieldValue(item.prop, $event)"
        />
      </el-form-item>
    </template>
    <el-form-item>
      <el-button type="primary" icon="search" @click="emit('query')">搜索</el-button>
      <el-button icon="refresh" @click="handleReset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import type { FormInstance } from "element-plus";
import type { TableSelectFieldValue, TableSelectFormItem, TableSelectQueryParams } from "./types";

type SelectValue =
  | string
  | number
  | boolean
  | Record<string, unknown>
  | Array<string | number | boolean>;
type DatePickerValue = string | number | Date | string[] | [Date, Date] | null | undefined;

const props = defineProps<{
  formItems: TableSelectFormItem[];
  queryParams: TableSelectQueryParams;
}>();

const emit = defineEmits<{
  query: [];
  reset: [];
}>();

const formRef = ref<FormInstance>();

function isInputItem(item: TableSelectFormItem) {
  if (item.attrs?.type === "number") {
    return false;
  }
  return item.type === "input" || !item.type;
}

function isNumberInputItem(item: TableSelectFormItem) {
  return item.attrs?.type === "number";
}

function getInputValue(prop: string): string | number | null | undefined {
  const value = props.queryParams[prop];
  if (typeof value === "string" || typeof value === "number" || value == null) {
    return value;
  }
  return String(value);
}

function getSelectValue(prop: string) {
  const value = props.queryParams[prop];
  if (value instanceof Date) {
    return value.toISOString();
  }
  return value;
}

function getTreeSelectValue(prop: string): SelectValue {
  const value = props.queryParams[prop];
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean" ||
    Array.isArray(value)
  ) {
    return value as SelectValue;
  }
  if (value && !(value instanceof Date)) {
    return value;
  }
  return "";
}

function getOptionValue(value: TableSelectFieldValue): SelectValue {
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean" ||
    Array.isArray(value)
  ) {
    return value as SelectValue;
  }
  if (value && !(value instanceof Date)) {
    return value;
  }
  return "";
}

function getDatePickerValue(prop: string): DatePickerValue {
  const value = props.queryParams[prop];
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    value instanceof Date ||
    value == null
  ) {
    return value;
  }
  if (Array.isArray(value)) {
    const dateValues = value.filter(isDatePickerArrayValue);
    return dateValues.every((item) => typeof item === "string") ? dateValues : undefined;
  }
  return undefined;
}

function isDatePickerArrayValue(value: unknown): value is string {
  return typeof value === "string";
}

function setFieldValue(prop: string, value: TableSelectFieldValue) {
  props.queryParams[prop] = value;
}

function handleReset() {
  formRef.value?.resetFields();
  emit("reset");
}
</script>
