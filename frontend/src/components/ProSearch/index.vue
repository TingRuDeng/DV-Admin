<template>
  <FilterPanel>
    <el-form ref="formRef" :model="model" v-bind="resolvedFormAttrs" class="ff-form ff-toolbar">
      <slot />

      <el-form-item v-if="showActions" class="ff-toolbar__actions">
        <slot name="actions" :submit="emitSubmit" :reset="handleReset">
          <el-button type="primary" icon="search" class="ff-button-primary" @click="emitSubmit">
            {{ submitText }}
          </el-button>
          <el-button icon="refresh" class="ff-button-secondary" @click="handleReset">
            {{ resetText }}
          </el-button>
        </slot>
      </el-form-item>
    </el-form>
  </FilterPanel>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { FormInstance, FormProps } from "element-plus";
import FilterPanel from "@/components/FilterPanel/index.vue";

const props = withDefaults(
  defineProps<{
    model: Record<string, unknown>;
    formAttrs?: Partial<FormProps>;
    showActions?: boolean;
    submitText?: string;
    resetText?: string;
  }>(),
  {
    showActions: true,
    submitText: "搜索",
    resetText: "重置",
  }
);

const emit = defineEmits<{
  submit: [];
  reset: [];
}>();

const formRef = ref<FormInstance>();

const resolvedFormAttrs = computed(() => {
  return {
    inline: true,
    ...props.formAttrs,
  };
});

function emitSubmit() {
  emit("submit");
}

function handleReset() {
  formRef.value?.resetFields();
  emit("reset");
}

defineExpose({
  formRef,
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate(),
  validate: (callback?: Parameters<FormInstance["validate"]>[0]) =>
    formRef.value?.validate(callback),
});
</script>
