<template>
  <div class="feedback">
    <el-button type="primary" size="small" @click="emit('confirm')">
      {{ confirmText }}
    </el-button>
    <el-button size="small" @click="emit('clear')">{{ t("tableSelect.clear") }}</el-button>
    <el-button size="small" @click="emit('close')">{{ t("tableSelect.close") }}</el-button>
  </div>
</template>

<script lang="ts" setup>
import { useI18n } from "vue-i18n";

defineProps<{
  confirmText: string;
}>();

const { t } = useI18n();

const emit = defineEmits<{
  confirm: [];
  clear: [];
  close: [];
}>();
</script>

<style scoped lang="scss">
.feedback {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}
</style>
