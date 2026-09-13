<!--
 * 基于 wangEditor-next 的富文本编辑器组件二次封装
 * 版权所有 © 2021-present 有来开源组织
 *
 * 开源协议：https://opensource.org/licenses/MIT
 * 项目地址：https://gitee.com/youlaiorg/vue3-element-admin
 *
 * 在使用时，请保留此注释，感谢您对开源的支持！
-->

<template>
  <div
    ref="editorRootRef"
    class="ff-rich-editor"
    style="z-index: 999; border: 1px solid var(--el-border-color)"
  >
    <!-- 工具栏 -->
    <Toolbar
      :editor="editorRef"
      mode="simple"
      :default-config="toolbarConfig"
      style="border-bottom: 1px solid var(--el-border-color)"
    />
    <!-- 编辑器 -->
    <Editor
      v-model="modelValue"
      :style="{ height: height, overflowY: 'hidden' }"
      :default-config="editorConfig"
      mode="simple"
      @on-created="handleCreated"
    />
  </div>
</template>

<script setup lang="ts">
import "@wangeditor-next/editor/dist/css/style.css";
import { Toolbar, Editor } from "@wangeditor-next/editor-for-vue";
import type {
  IDomEditor,
  IEditorConfig,
  IToolbarConfig,
  IUploadConfig,
} from "@wangeditor-next/editor";

// 文件上传 API
import FileAPI from "@/api/file-api";
import { bindEditorIcons } from "./editor-icons";
import { syncEditorLanguage } from "./editor-language";
import { useI18n } from "vue-i18n";

const { t, locale } = useI18n();

type InsertImageFn =
  NonNullable<IUploadConfig["customUpload"]> extends (
    _file: File,
    insertFn: infer TInsertFn,
    _editor: IDomEditor
  ) => void
    ? TInsertFn
    : never;

type UploadImageConfig = IUploadConfig & {
  base64LimitSize: number;
};

defineProps({
  height: {
    type: String,
    default: "500px",
  },
});
// 双向绑定
const modelValue = defineModel("modelValue", {
  type: String,
  required: false,
});

// 编辑器实例，必须用 shallowRef，重要！
const editorRef = shallowRef<IDomEditor>();
const editorRootRef = ref<HTMLElement>();
let icons: ReturnType<typeof bindEditorIcons> | undefined;
const refreshIcons = () => icons?.refresh();

onMounted(() => {
  if (editorRootRef.value) {
    icons = bindEditorIcons(
      editorRootRef.value,
      () => editorRef.value?.isFullScreen ?? false,
      (key) => {
        if (key === "group-image") return t("upload.image");
        if (key === "fullScreen") {
          return t(
            editorRef.value?.isFullScreen ? "navbar.exitFullscreen" : "navbar.enterFullscreen"
          );
        }
        return undefined;
      }
    );
  }
});

// 工具栏配置
const toolbarConfig = ref<Partial<IToolbarConfig>>({ excludeKeys: ["emotion"] });

// 编辑器配置
const uploadImageConfig: UploadImageConfig = {
  metaWithUrl: false,
  base64LimitSize: 0,
  onSuccess() {},
  onFailed() {},
  onError() {},
  customUpload(file: File, insertFn: InsertImageFn) {
    // 上传图片成功后沿用当前插入参数顺序，避免改变富文本内容表现。
    FileAPI.uploadFile(file).then((res) => {
      insertFn(res.url, res.name, res.url);
    });
  },
};

const editorConfig = ref<Partial<IEditorConfig>>({
  placeholder: t("common.editorPlaceholder"),
  MENU_CONF: {
    uploadImage: uploadImageConfig,
  },
});

watch(
  locale,
  () => {
    syncEditorLanguage(locale.value);
    const placeholder = t("common.editorPlaceholder");
    editorConfig.value.placeholder = placeholder;
    const editor = editorRef.value;
    if (editor && !editor.isDestroyed) {
      editor.getConfig().placeholder = placeholder;
      // The native placeholder is cached outside the editable document. Updating
      // defaultConfig or the editor view does not update an existing label.
      const label = editorRootRef.value?.querySelector(
        ".w-e-text-container > .w-e-text-placeholder"
      );
      if (label) label.textContent = placeholder;
      refreshIcons();
    }
  },
  { immediate: true, flush: "post" }
);

// 记录 editor 实例，重要！
const handleCreated = (editor: IDomEditor) => {
  editorRef.value = editor;
  editor.on("fullscreen", refreshIcons);
  editor.on("unFullScreen", refreshIcons);
};

// 组件销毁时，也及时销毁编辑器，重要！
onBeforeUnmount(() => {
  icons?.dispose();
  const editor = editorRef.value;
  if (editor == null) return;
  editor.off("fullscreen", refreshIcons);
  editor.off("unFullScreen", refreshIcons);
  editor.destroy();
});
</script>

<style scoped lang="scss">
.ff-rich-editor {
  border-radius: var(--ff-radius-control);

  :deep(.w-e-bar svg[data-editor-lucide]),
  :deep(.w-e-hover-bar svg[data-editor-lucide]) {
    width: 18px;
    height: 18px;
    stroke: currentColor;
  }

  :deep(.w-e-bar button:focus-visible) {
    outline: 2px solid var(--el-color-primary);
    outline-offset: -2px;
  }
}
</style>
