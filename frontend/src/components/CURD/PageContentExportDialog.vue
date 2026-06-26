<template>
  <ProDialog
    v-model="visible"
    title="导出数据"
    width="600px"
    :dialog-attrs="{ alignCenter: true }"
    @close="handleClose"
  >
    <!-- 滚动 -->
    <el-scrollbar max-height="60vh">
      <!-- 表单 -->
      <el-form
        ref="exportsFormRef"
        style="padding-right: var(--el-dialog-padding-primary)"
        :model="exportsFormData"
        :rules="exportsFormRules"
      >
        <el-form-item label="文件名" prop="filename">
          <el-input v-model="exportsFormData.filename" clearable />
        </el-form-item>
        <el-form-item label="工作表名" prop="sheetname">
          <el-input v-model="exportsFormData.sheetname" clearable />
        </el-form-item>
        <el-form-item label="数据源" prop="origin">
          <el-select v-model="exportsFormData.origin">
            <el-option label="当前数据 (当前页的数据)" :value="EXPORT_ORIGIN_CURRENT" />
            <el-option
              label="选中数据 (所有选中的数据)"
              :value="EXPORT_ORIGIN_SELECTED"
              :disabled="selectionCount <= 0"
            />
            <el-option
              label="全量数据 (所有分页的数据)"
              :value="EXPORT_ORIGIN_REMOTE"
              :disabled="!hasRemoteAction"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="字段" prop="fields">
          <el-checkbox-group v-model="exportsFormData.fields">
            <template v-for="col in cols" :key="col.prop">
              <el-checkbox v-if="col.prop" :value="col.prop" :label="col.label" />
            </template>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
    </el-scrollbar>
    <!-- 弹窗底部操作按钮 -->
    <template #footer>
      <div style="padding-right: var(--el-dialog-padding-primary)">
        <el-button type="primary" @click="handleSubmit">确 定</el-button>
        <el-button @click="handleClose">取 消</el-button>
      </div>
    </template>
  </ProDialog>
</template>

<script setup lang="ts">
import ProDialog from "@/components/ProDialog/index.vue";
import { useThrottleFn } from "@vueuse/core";
import type { FormInstance, FormRules } from "element-plus";
import { computed, nextTick, reactive, ref } from "vue";
import type { IContentConfig } from "./types";

const EXPORT_ORIGIN_CURRENT = "current";
const EXPORT_ORIGIN_SELECTED = "selected";
const EXPORT_ORIGIN_REMOTE = "remote";

type ExportOrigin =
  | typeof EXPORT_ORIGIN_CURRENT
  | typeof EXPORT_ORIGIN_SELECTED
  | typeof EXPORT_ORIGIN_REMOTE;

export interface PageContentExportPayload {
  filename: string;
  sheetname: string;
  fields: string[];
  origin: ExportOrigin;
}

const visible = defineModel<boolean>({ required: true });
const props = defineProps<{
  cols: IContentConfig["cols"];
  selectionCount: number;
  hasRemoteAction: boolean;
}>();

const emit = defineEmits<{
  submit: [data: PageContentExportPayload];
}>();

const selectableFields = computed(() =>
  props.cols.flatMap((col) => (col.prop !== undefined ? [col.prop] : []))
);
const exportsFormRef = ref<FormInstance>();
const exportsFormData = reactive<PageContentExportPayload>({
  filename: "",
  sheetname: "",
  fields: [...selectableFields.value],
  origin: EXPORT_ORIGIN_CURRENT,
});
const exportsFormRules: FormRules = {
  fields: [{ required: true, message: "请选择字段" }],
  origin: [{ required: true, message: "请选择数据源" }],
};

function resetFormData() {
  exportsFormData.filename = "";
  exportsFormData.sheetname = "";
  exportsFormData.fields = [...selectableFields.value];
  exportsFormData.origin = EXPORT_ORIGIN_CURRENT;
}

function handleClose() {
  visible.value = false;
  exportsFormRef.value?.resetFields();
  resetFormData();
  nextTick(() => {
    exportsFormRef.value?.clearValidate();
  });
}

const handleSubmit = useThrottleFn(() => {
  exportsFormRef.value?.validate((valid: boolean) => {
    if (!valid) return;
    emit("submit", {
      filename: exportsFormData.filename,
      sheetname: exportsFormData.sheetname,
      fields: [...exportsFormData.fields],
      origin: exportsFormData.origin,
    });
    handleClose();
  });
}, 3000);
</script>
