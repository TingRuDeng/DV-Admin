<template>
  <ProDialog
    v-model="visible"
    :title="t('dataTransfer.importTitle')"
    width="600px"
    :dialog-attrs="{ alignCenter: true }"
    @close="close"
  >
    <!-- 滚动 -->
    <el-scrollbar max-height="60vh">
      <!-- 表单 -->
      <el-form
        ref="importFormRef"
        style="padding-right: var(--el-dialog-padding-primary)"
        :model="importFormData"
        :rules="importFormRules"
      >
        <el-form-item :label="t('dataTransfer.file')" prop="files">
          <el-upload
            ref="uploadRef"
            v-model:file-list="importFormData.files"
            class="w-full"
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
            :drag="true"
            :limit="1"
            :auto-upload="false"
            :on-exceed="handleFileExceed"
          >
            <AppIcon name="upload" :size="38" class="el-icon--upload" />
            <div class="el-upload__text">
              <span>{{ t("dataTransfer.dropFile") }}</span>
              <em>{{ t("dataTransfer.clickUpload") }}</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                *.xlsx / *.xls
                <el-link
                  v-if="hasImportTemplate"
                  type="primary"
                  :icon="resolveAppIcon('download')"
                  underline="never"
                  @click="emit('downloadTemplate')"
                >
                  {{ t("dataTransfer.downloadTemplate") }}
                </el-link>
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
    </el-scrollbar>
    <!-- 弹窗底部操作按钮 -->
    <template #footer>
      <div style="padding-right: var(--el-dialog-padding-primary)">
        <el-button
          type="primary"
          :disabled="importFormData.files.length === 0"
          @click="handleSubmit"
        >
          {{ t("common.confirm") }}
        </el-button>
        <el-button @click="close">{{ t("common.cancel") }}</el-button>
      </div>
    </template>
  </ProDialog>
</template>

<script setup lang="ts">
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
import ProDialog from "@/components/ProDialog/index.vue";
import AppIcon from "@/components/AppIcon/index.vue";
import { useThrottleFn } from "@vueuse/core";
import {
  genFileId,
  type FormInstance,
  type FormRules,
  type UploadInstance,
  type UploadRawFile,
  type UploadUserFile,
} from "element-plus";
import { nextTick, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";

export interface PageContentImportPayload {
  file: File;
  isFileImport: boolean;
}

const visible = defineModel<boolean>({ required: true });
defineProps<{
  hasImportTemplate: boolean;
}>();

const emit = defineEmits<{
  submit: [data: PageContentImportPayload];
  downloadTemplate: [];
}>();

const { t } = useI18n();

let isFileImport = false;
const uploadRef = ref<UploadInstance>();
const importFormRef = ref<FormInstance>();
const importFormData = reactive<{
  files: UploadUserFile[];
}>({
  files: [],
});
const importFormRules: FormRules = {
  files: [{ required: true, message: () => t("dataTransfer.selectFile") }],
};

function open(isFile = false) {
  isFileImport = isFile;
  visible.value = true;
}

function close() {
  visible.value = false;
  importFormRef.value?.resetFields();
  nextTick(() => {
    importFormRef.value?.clearValidate();
  });
}

function handleFileExceed(files: File[]) {
  uploadRef.value?.clearFiles();
  const file = files[0] as UploadRawFile;
  file.uid = genFileId();
  uploadRef.value?.handleStart(file);
}

const handleSubmit = useThrottleFn(() => {
  importFormRef.value?.validate((valid: boolean) => {
    if (!valid) return;
    emit("submit", {
      file: importFormData.files[0].raw as File,
      isFileImport,
    });
  });
}, 3000);

defineExpose({ open, close });
</script>
