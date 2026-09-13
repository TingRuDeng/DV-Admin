<template>
  <div>
    <ProFormDrawer
      ref="importFormRef"
      v-model="visible"
      :title="t('userImport.title')"
      :model="importFormData"
      :rules="importFormRules"
      :loading="uploading"
      size="600px"
      label-width="90px"
      @submit="handleUpload"
      @close="handleClose"
    >
      <el-form-item :label="t('userImport.fileName')" prop="files" :error="fileError">
        <el-upload
          ref="uploadRef"
          v-model:file-list="importFormData.files"
          class="w-full"
          accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          :drag="true"
          :limit="1"
          :auto-upload="false"
          :on-exceed="handleFileExceed"
          :on-change="handleFileChange"
          :on-remove="clearFileError"
        >
          <AppIcon name="upload" :size="38" class="el-icon--upload" />
          <div class="el-upload__text">
            {{ t("userImport.dropFile") }}
            <em>{{ t("userImport.clickUpload") }}</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              <el-link type="primary" underline="never" @click="handleDownloadTemplate">
                <template #icon><AppIcon name="download" :size="14" /></template>
                {{ t("userImport.downloadTemplate") }}
              </el-link>
            </div>
          </template>
        </el-upload>
      </el-form-item>

      <template #footer="{ submit, cancel }">
        <div class="dialog-footer flex justify-end gap-2">
          <el-button v-if="resultData.length > 0" type="primary" @click="handleShowResult">
            {{ t("userImport.errorDetails") }}
          </el-button>
          <el-button
            type="primary"
            :loading="uploading"
            :disabled="importFormData.files.length === 0"
            @click="submit"
          >
            {{ t("userImport.confirm") }}
          </el-button>
          <el-button :disabled="uploading" @click="cancel">{{ t("userImport.cancel") }}</el-button>
        </div>
      </template>
    </ProFormDrawer>

    <ProDialog
      v-model="resultVisible"
      :title="t('userImport.resultTitle')"
      width="600px"
      :show-confirm-button="false"
      :cancel-text="t('userImport.close')"
    >
      <el-alert
        :title="t('userImport.summary', { success: validCount, failed: invalidCount })"
        :type="validCount > 0 ? 'warning' : 'error'"
        :closable="false"
      />
      <el-table :data="resultData" style="width: 100%; max-height: 400px">
        <el-table-column
          prop="index"
          align="center"
          width="100"
          type="index"
          :label="t('userImport.index')"
        />
        <el-table-column prop="message" :label="t('userImport.errorMessage')" min-width="260">
          <template #default="scope">
            {{ scope.row }}
          </template>
        </el-table-column>
      </el-table>
      <template #footer="{ cancel }">
        <div class="dialog-footer">
          <el-button @click="cancel">{{ t("userImport.close") }}</el-button>
        </div>
      </template>
    </ProDialog>
  </div>
</template>

<script lang="ts" setup>
import AppIcon from "@/components/AppIcon/index.vue";
import ProDialog from "@/components/ProDialog/index.vue";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import { ElMessage, type UploadInstance, type UploadUserFile } from "element-plus";
import UserAPI from "@/api/system/user-api";
import { createLogger } from "@/utils/logger";
import { downloadEncodedFile } from "@/utils/file-download";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const userImportLogger = createLogger("UserImport");
const props = defineProps<{
  deptId?: string | number;
}>();

const emit = defineEmits<{
  "import-success": [];
}>();
const visible = defineModel("modelValue", {
  type: Boolean,
  required: true,
  default: false,
});

const resultVisible = ref(false);
const resultData = ref<string[]>([]);
const invalidCount = ref(0);
const validCount = ref(0);
const uploading = ref(false);
const fileErrorKey = ref("");
const fileError = computed(() => (fileErrorKey.value ? t(fileErrorKey.value) : ""));

const importFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const uploadRef = ref<UploadInstance>();

const importFormData = reactive<{
  files: UploadUserFile[];
}>({
  files: [],
});

watch(visible, (newValue) => {
  if (newValue) {
    resultData.value = [];
    resultVisible.value = false;
    invalidCount.value = 0;
    validCount.value = 0;
    clearFileError();
  }
});

const importFormRules = computed(() => ({
  files: [{ required: true, message: t("userImport.fileRequired"), trigger: "blur" }],
}));

// 文件超出个数限制
const handleFileExceed = () => {
  ElMessage.warning(t("userImport.singleFileOnly"));
};

function clearFileError() {
  fileErrorKey.value = "";
}

function handleFileChange(file: UploadUserFile) {
  if (!file.name?.toLowerCase().endsWith(".xlsx")) {
    importFormData.files = [];
    fileErrorKey.value = "userImport.invalidFileType";
    return;
  }
  clearFileError();
}

// 下载导入模板
const handleDownloadTemplate = async () => {
  try {
    downloadEncodedFile(await UserAPI.downloadTemplate());
  } catch (error: unknown) {
    userImportLogger.error("用户导入模板下载失败:", error);
    ElMessage.error(t("userImport.templateDownloadFailed"));
  }
};

// 上传文件
const handleUpload = async () => {
  const selectedFile = importFormData.files[0];
  if (!selectedFile?.raw) {
    fileErrorKey.value = "userImport.fileRequired";
    return;
  }
  if (!selectedFile.name?.toLowerCase().endsWith(".xlsx")) {
    fileErrorKey.value = "userImport.invalidFileType";
    return;
  }

  clearFileError();
  uploading.value = true;
  resultVisible.value = false;
  resultData.value = [];
  invalidCount.value = 0;
  validCount.value = 0;
  try {
    const result = await UserAPI.import(props.deptId, selectedFile.raw);
    if (result.validCount > 0) {
      emit("import-success");
    }
    if (result.invalidCount > 0) {
      const summary = t("userImport.summary", {
        success: result.validCount,
        failed: result.invalidCount,
      });
      if (result.validCount > 0) {
        ElMessage.warning(t("userImport.partialSuccess", { summary }));
      } else {
        ElMessage.error(t("userImport.failed", { summary }));
      }
      resultVisible.value = true;
      resultData.value = result.messageList;
      invalidCount.value = result.invalidCount;
      validCount.value = result.validCount;
    } else if (result.validCount > 0) {
      ElMessage.success(t("userImport.success", { count: result.validCount }));
      handleClose();
    } else {
      ElMessage.warning(t("userImport.emptyResult"));
    }
  } catch (error: unknown) {
    userImportLogger.error("用户导入失败:", error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    ElMessage.error(t("userImport.uploadFailed", { message: errorMessage }));
  } finally {
    uploading.value = false;
  }
};

// 显示错误信息
const handleShowResult = () => {
  resultVisible.value = true;
};

// 关闭弹窗
const handleClose = () => {
  clearFileError();
  importFormRef.value?.resetFields();
  importFormRef.value?.clearValidate();
  importFormData.files = [];
  visible.value = false;
};
</script>
