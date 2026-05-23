<template>
  <div class="feedback">
    <el-button type="primary" size="small" @click="emit('confirm')">
      {{ confirmText }}
    </el-button>
    <el-button size="small" @click="emit('clear')">清 空</el-button>
    <el-button size="small" @click="emit('close')">关 闭</el-button>
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  confirmText: string;
}>();

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
