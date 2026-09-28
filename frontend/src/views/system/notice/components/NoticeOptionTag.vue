<template>
  <el-tag v-if="option" :type="option.tagType" effect="light" :size="size">
    {{ option.label }}
  </el-tag>
  <el-tag v-else type="info" effect="light" :size="size">
    {{ value === undefined || value === null ? "-" : String(value) }}
  </el-tag>
</template>

<script setup lang="ts">
import { getNoticeOption, type NoticeOptionKind } from "@/constants/notice-options";

defineOptions({ name: "NoticeOptionTag" });

const props = withDefaults(
  defineProps<{
    kind: NoticeOptionKind;
    value?: string | number;
    size?: "default" | "large" | "small";
  }>(),
  { size: "default" }
);

const option = computed(() => getNoticeOption(props.kind, props.value));
</script>
