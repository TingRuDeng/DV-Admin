<template>
  <el-tag
    v-if="statusMeta"
    :type="statusMeta.type"
    effect="light"
    class="ff-status-tag"
    :class="statusMeta.className"
  >
    {{ statusMeta.label }}
  </el-tag>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
defineOptions({
  name: "NoticeStatusTag",
});

type NoticeStatusKind = "target" | "publish";
type NoticeStatusTagType = "success" | "warning" | "info";

interface NoticeStatusMeta {
  label: string;
  type: NoticeStatusTagType;
  className: string;
}

const STATUS_META_MAP = computed<Record<NoticeStatusKind, Record<number, NoticeStatusMeta>>>(
  () => ({
    target: {
      1: { label: t("system.allUsers"), type: "warning", className: "warning" },
      2: { label: t("system.specifiedUsers"), type: "success", className: "success" },
    },
    publish: {
      [-1]: { label: t("system.revokedStatus"), type: "warning", className: "warning" },
      0: { label: t("system.unpublished"), type: "info", className: "info" },
      1: { label: t("system.publishedStatus"), type: "success", className: "success" },
    },
  })
);

const props = defineProps<{
  kind: NoticeStatusKind;
  value?: number;
}>();

// 根据状态类型和值生成标签元信息，未知值不渲染标签。
const statusMeta = computed(() => {
  if (typeof props.value !== "number") {
    return undefined;
  }

  return STATUS_META_MAP.value[props.kind][props.value];
});
</script>
