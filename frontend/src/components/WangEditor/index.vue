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
  <div style="z-index: 999; border: 1px solid var(--el-border-color)">
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

// 工具栏配置
const toolbarConfig = ref<Partial<IToolbarConfig>>({});

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
  placeholder: "请输入内容...",
  MENU_CONF: {
    uploadImage: uploadImageConfig,
  },
});

// 记录 editor 实例，重要！
const handleCreated = (editor: IDomEditor) => {
  editorRef.value = editor;
};

// 组件销毁时，也及时销毁编辑器，重要！
onBeforeUnmount(() => {
  const editor = editorRef.value;
  if (editor == null) return;
  editor.destroy();
});
</script>
