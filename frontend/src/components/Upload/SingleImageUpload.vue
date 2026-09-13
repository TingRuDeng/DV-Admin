<!-- 单图上传组件 -->
<template>
  <el-upload
    class="single-upload"
    list-type="picture-card"
    :show-file-list="false"
    :accept="props.accept"
    :before-upload="handleBeforeUpload"
    :http-request="handleUpload"
    :on-success="onSuccess"
    :on-error="onError"
  >
    <template #default>
      <template v-if="modelValue">
        <el-image
          class="single-upload__image"
          :src="modelValue"
          :preview-src-list="[modelValue]"
          @click.stop="handlePreview"
        />
        <button
          type="button"
          class="single-upload__delete-btn"
          :aria-label="t('upload.deleteImage')"
          :title="t('upload.deleteImage')"
          @click.stop="handleDelete"
        >
          <AppIcon name="x" :size="16" />
        </button>
      </template>
      <template v-else>
        <AppIcon name="plus" :size="24" />
        <span class="sr-only">{{ t("upload.image") }}</span>
      </template>
    </template>
  </el-upload>
</template>

<script setup lang="ts">
import { UploadRawFile, UploadRequestOptions } from "element-plus";
import FileAPI, { FileInfo } from "@/api/file-api";
import { getUploadErrorMessage } from "@/components/Upload/uploadError";
import AppIcon from "@/components/AppIcon/index.vue";

const { t } = useI18n();

const props = defineProps({
  /**
   * 请求携带的额外参数
   */
  data: {
    type: Object,
    default: () => {
      return {};
    },
  },
  /**
   * 上传文件的参数名
   */
  name: {
    type: String,
    default: "file",
  },
  /**
   * 最大文件大小（单位：M）
   */
  maxFileSize: {
    type: Number,
    default: 10,
  },

  /**
   * 上传图片格式，默认支持所有图片(image/*)，指定格式示例：'.png,.jpg,.jpeg,.gif,.bmp'
   */
  accept: {
    type: String,
    default: "image/*",
  },

  /**
   * 自定义样式，用于设置组件的宽度和高度等其他样式
   */
  style: {
    type: Object,
    default: () => {
      return {
        width: "150px",
        height: "150px",
      };
    },
  },
});

const modelValue = defineModel("modelValue", {
  type: String,
  default: () => "",
});

/**
 * 限制用户上传文件的格式和大小
 */
function handleBeforeUpload(file: UploadRawFile) {
  // 校验文件类型：虽然 accept 属性限制了用户在文件选择器中可选的文件类型，但仍需在上传时再次校验文件实际类型，确保符合 accept 的规则
  const acceptTypes = props.accept.split(",").map((type) => type.trim());

  // 检查文件格式是否符合 accept
  const isValidType = acceptTypes.some((type) => {
    if (type === "image/*") {
      // 如果是 image/*，检查 MIME 类型是否以 "image/" 开头
      return file.type.startsWith("image/");
    } else if (type.startsWith(".")) {
      // 如果是扩展名 (.png, .jpg)，检查文件名是否以指定扩展名结尾
      return file.name.toLowerCase().endsWith(type);
    } else {
      // 如果是具体的 MIME 类型 (image/png, image/jpeg)，检查是否完全匹配
      return file.type === type;
    }
  });

  if (!isValidType) {
    ElMessage.warning(t("upload.invalidFormat", { types: props.accept }));
    return false;
  }

  // 限制文件大小
  if (file.size > props.maxFileSize * 1024 * 1024) {
    ElMessage.warning(t("upload.imageTooLarge", { size: props.maxFileSize }));
    return false;
  }
  return true;
}

/*
 * 上传图片
 */
function handleUpload(options: UploadRequestOptions) {
  return new Promise((resolve, reject) => {
    const file = options.file;

    const formData = new FormData();
    formData.append(props.name, file);

    // 处理附加参数
    Object.keys(props.data).forEach((key) => {
      formData.append(key, props.data[key]);
    });

    FileAPI.upload(formData)
      .then((data) => {
        resolve(data);
      })
      .catch((error) => {
        reject(error);
      });
  });
}

/**
 * 预览图片
 */
function handlePreview() {
  // 预览交由 el-upload 内部处理，这里仅保留事件占位。
}

/**
 * 删除图片
 */
function handleDelete() {
  modelValue.value = "";
}

/**
 * 上传成功回调
 *
 * @param fileInfo 上传成功后的文件信息
 */
const onSuccess = (fileInfo: FileInfo) => {
  ElMessage.success(t("upload.success"));
  modelValue.value = fileInfo.url;
};

/**
 * 上传失败回调
 */
const onError = (error: unknown) => {
  ElMessage.error(`${t("upload.failed")}: ${getUploadErrorMessage(error)}`);
};
</script>

<style scoped lang="scss">
:deep(.el-upload--picture-card) {
  position: relative;
  width: v-bind("props.style.width ?? '150px'");
  height: v-bind("props.style.height ?? '150px'");
}

.single-upload {
  &__image {
    border-radius: 6px;
  }

  &__delete-btn {
    position: absolute;
    top: 1px;
    right: 1px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 3px;
    font-size: 16px;
    color: var(--el-text-color-primary);
    cursor: pointer;
    background: var(--el-bg-color-overlay);
    border: 0;
    border-radius: 100%;

    &:hover,
    &:focus-visible {
      color: var(--el-color-danger);
    }
  }
}
</style>
