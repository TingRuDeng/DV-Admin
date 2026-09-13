<template>
  <el-drawer
    v-model="drawerVisible"
    :title="title"
    :size="size"
    :append-to-body="appendToBody"
    class="ff-drawer"
    v-bind="drawerAttrs"
    @close="handleClose"
  >
    <div v-loading="loading">
      <slot />
    </div>

    <template v-if="showFooter" #footer>
      <slot name="footer" :submit="handleSubmit" :cancel="handleCancel">
        <div class="dialog-footer flex justify-end gap-2">
          <el-button v-if="showCancelButton" class="ff-button-secondary" @click="handleCancel">
            {{ cancelText ?? t("common.cancel") }}
          </el-button>
          <el-button
            v-if="showConfirmButton"
            type="primary"
            class="ff-button-primary"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ confirmText ?? t("common.confirm") }}
          </el-button>
        </div>
      </slot>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { DrawerProps } from "element-plus";

const { t } = useI18n();

const props = withDefaults(
  defineProps<{
    modelValue: boolean;
    title?: string;
    size?: string | number;
    loading?: boolean;
    appendToBody?: boolean;
    showFooter?: boolean;
    showConfirmButton?: boolean;
    showCancelButton?: boolean;
    confirmText?: string;
    cancelText?: string;
    drawerAttrs?: Partial<DrawerProps>;
  }>(),
  {
    title: "",
    size: "600px",
    loading: false,
    appendToBody: false,
    showFooter: true,
    showConfirmButton: true,
    showCancelButton: true,
    drawerAttrs: () => ({}),
  }
);

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  submit: [];
  cancel: [];
  close: [];
}>();

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
</script>
