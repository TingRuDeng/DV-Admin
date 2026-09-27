<template>
  <div v-if="password" class="password-strength" :aria-label="ariaLabel" role="status">
    <div class="password-strength__track">
      <div
        class="password-strength__fill"
        :class="`password-strength__fill--${level}`"
        :style="{ width: `${score * 25}%` }"
      />
    </div>
    <span class="password-strength__label" :class="`password-strength__label--${level}`">
      {{ label }}
    </span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  password: string;
}>();

const { t } = useI18n();

/**
 * 简单强度评分（0-4）：
 * +1 长度 ≥ 8；+1 长度 ≥ 12；+1 包含数字；+1 包含大写或特殊字符
 */
const score = computed(() => {
  const p = props.password;
  if (!p) return 0;
  let s = 0;
  if (p.length >= 8) s++;
  if (p.length >= 12) s++;
  if (/\d/.test(p)) s++;
  if (/[A-Z!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(p)) s++;
  return Math.max(1, s); // 有内容至少 1 格
});

const level = computed(() => {
  const map = ["", "weak", "fair", "good", "strong"] as const;
  return map[score.value];
});

const label = computed(() => t(`passwordStrength.${level.value}`));
const ariaLabel = computed(() => t("passwordStrength.aria", { label: label.value }));
</script>

<style lang="scss" scoped>
.password-strength {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 4px;
}

.password-strength__track {
  flex: 1;
  height: 4px;
  overflow: hidden;
  background: var(--ff-shell-border);
  border-radius: 2px;
}

.password-strength__fill {
  height: 100%;
  border-radius: 2px;
  transition:
    width 0.3s var(--ff-ease-out),
    background-color 0.3s ease;

  &--weak {
    background: var(--el-color-danger);
  }

  &--fair {
    background: var(--el-color-warning);
  }

  &--good {
    background: var(--el-color-success-light-3);
  }

  &--strong {
    background: var(--el-color-success);
  }
}

.password-strength__label {
  flex: none;
  font-size: 0.75rem;

  &--weak {
    color: var(--el-color-danger);
  }

  &--fair {
    color: var(--el-color-warning);
  }

  &--good {
    color: var(--el-color-success-light-3);
  }

  &--strong {
    color: var(--el-color-success);
  }
}
</style>
