<!-- 复制组件 -->
<template>
  <el-button
    link
    :style="style"
    :aria-label="t('common.copy')"
    :title="t('common.copy')"
    @click="handleClipboard"
  >
    <slot>
      <AppIcon name="copy" :size="16" color="var(--el-color-primary)" />
    </slot>
  </el-button>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import { createLogger } from "@/utils/logger";

defineOptions({
  name: "CopyButton",
  inheritAttrs: false,
});

const copyButtonLogger = createLogger("CopyButton");
const { t } = useI18n();

const props = defineProps({
  text: {
    type: String,
    default: "",
  },
  style: {
    type: Object,
    default: () => ({}),
  },
});

function handleClipboard() {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    // 使用 Clipboard API
    navigator.clipboard
      .writeText(props.text)
      .then(() => {
        ElMessage.success(t("common.copySuccess"));
      })
      .catch((error) => {
        ElMessage.warning(t("common.copyFailed"));
        copyButtonLogger.error("复制失败:", error);
      });
  } else {
    // 兼容性处理（useClipboard 有兼容性问题）
    const input = document.createElement("input");
    input.style.position = "absolute";
    input.style.left = "-9999px";
    input.setAttribute("value", props.text);
    document.body.appendChild(input);
    input.select();
    try {
      const successful = document.execCommand("copy");
      if (successful) {
        ElMessage.success(t("common.copySuccess"));
      } else {
        ElMessage.warning(t("common.copyFailed"));
      }
    } catch (err) {
      ElMessage.error(t("common.copyFailed"));
      copyButtonLogger.error("兼容复制失败:", err);
    } finally {
      document.body.removeChild(input);
    }
  }
}
</script>
