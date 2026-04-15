<template>
  <el-drawer
    v-model="drawerVisible"
    :title="title"
    append-to-body
    class="ff-drawer"
    :size="size"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      v-loading="loading"
      :model="model"
      :rules="rules"
      :label-width="labelWidth"
      class="ff-form"
      v-bind="formAttrs"
    >
      <slot />
    </el-form>

    <template #footer>
      <slot name="footer" :submit="handleSubmit" :cancel="handleCancel">
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="ff-button-secondary" @click="handleCancel">取 消</el-button>
          <el-button
            type="primary"
            class="ff-button-primary"
            :loading="loading"
            @click="handleSubmit"
          >
            确 定
          </el-button>
        </div>
      </slot>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { FormInstance, FormProps, FormRules } from "element-plus";
import type { ProFormDrawerExpose } from "./types";

const props = withDefaults(
  defineProps<{
    modelValue: boolean;
    title: string;
    model: Record<string, unknown>;
    rules?: FormRules;
    loading?: boolean;
    size?: string | number;
    labelWidth?: string | number;
    formAttrs?: Partial<FormProps>;
  }>(),
  {
    rules: () => ({}),
    loading: false,
    size: "600px",
    labelWidth: "80px",
    formAttrs: () => ({}),
  }
);

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  submit: [];
  cancel: [];
  close: [];
}>();

const formRef = ref<FormInstance>();

const drawerVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit("update:modelValue", value),
});

function handleSubmit() {
  emit("submit");
}

function handleCancel() {
  emit("cancel");
  drawerVisible.value = false;
}

function handleClose() {
  emit("close");
}

defineExpose<ProFormDrawerExpose>({
  formRef,
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate(),
  validate: (callback?: Parameters<FormInstance["validate"]>[0]) =>
    formRef.value?.validate(callback),
});
</script>
