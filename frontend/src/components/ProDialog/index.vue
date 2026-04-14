<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :append-to-body="appendToBody"
    :show-close="showClose"
    class="ff-dialog"
    v-bind="dialogAttrs"
    @close="handleClose"
  >
    <template v-if="hasHeaderSlot" #header>
      <slot name="header" />
    </template>

    <div v-loading="loading">
      <slot />
    </div>

    <template v-if="showFooter" #footer>
      <slot name="footer" :submit="handleSubmit" :cancel="handleCancel">
        <div class="dialog-footer flex justify-end gap-2">
          <el-button v-if="showCancelButton" class="ff-button-secondary" @click="handleCancel">
            {{ cancelText }}
          </el-button>
          <el-button
            v-if="showConfirmButton"
            type="primary"
            class="ff-button-primary"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ confirmText }}
          </el-button>
        </div>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, useSlots } from "vue";
import type { DialogProps } from "element-plus";

const props = withDefaults(
  defineProps<{
    modelValue: boolean;
    title?: string;
    width?: string | number;
    loading?: boolean;
    appendToBody?: boolean;
    showClose?: boolean;
    showFooter?: boolean;
    showConfirmButton?: boolean;
    showCancelButton?: boolean;
    confirmText?: string;
    cancelText?: string;
    dialogAttrs?: Partial<DialogProps>;
  }>(),
  {
    title: "",
    width: "600px",
    loading: false,
    appendToBody: false,
    showClose: true,
    showFooter: true,
    showConfirmButton: true,
    showCancelButton: true,
    confirmText: "确 定",
    cancelText: "取 消",
    dialogAttrs: () => ({}),
  }
);

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  submit: [];
  cancel: [];
  close: [];
}>();

const slots = useSlots();
const hasHeaderSlot = computed(() => Boolean(slots.header));

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit("update:modelValue", value),
});

function handleSubmit() {
  emit("submit");
}

function handleCancel() {
  emit("cancel");
  dialogVisible.value = false;
}

function handleClose() {
  emit("close");
}
</script>
