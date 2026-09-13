<template>
  <el-tag class="ff-status-tag" :class="statusMeta.className" :type="statusMeta.type">
    {{ statusMeta.label }}
  </el-tag>
</template>

<script setup lang="ts">
defineOptions({
  name: "UserStatusTag",
});

const USER_STATUS_META_MAP: Record<
  number,
  { labelKey: "user.active" | "user.inactive"; type: "success" | "info"; className: string }
> = {
  0: { labelKey: "user.inactive", type: "info", className: "info" },
  1: { labelKey: "user.active", type: "success", className: "success" },
};

const props = defineProps<{
  value?: number;
}>();

const { t } = useI18n();

// 用户状态只有启用和禁用两类，未知值按禁用样式展示以匹配原页面逻辑。
const statusMeta = computed(() => {
  const meta = USER_STATUS_META_MAP[props.value ?? 0] ?? USER_STATUS_META_MAP[0];
  return { ...meta, label: t(meta.labelKey) };
});
</script>
