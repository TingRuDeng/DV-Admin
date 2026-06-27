<template>
  <el-tag class="ff-status-tag" :class="statusMeta.className" :type="statusMeta.type">
    {{ statusMeta.label }}
  </el-tag>
</template>

<script setup lang="ts">
defineOptions({
  name: "UserStatusTag",
});

type UserStatusTagType = "success" | "info";

interface UserStatusMeta {
  label: string;
  type: UserStatusTagType;
  className: string;
}

const USER_STATUS_META_MAP: Record<number, UserStatusMeta> = {
  0: { label: "禁用", type: "info", className: "info" },
  1: { label: "正常", type: "success", className: "success" },
};

const props = defineProps<{
  value?: number;
}>();

// 用户状态只有启用和禁用两类，未知值按禁用样式展示以匹配原页面逻辑。
const statusMeta = computed(
  () => USER_STATUS_META_MAP[props.value ?? 0] ?? USER_STATUS_META_MAP[0]
);
</script>
