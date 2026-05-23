<template>
  <el-card shadow="hover" class="dict-card">
    <template #header>
      <div class="flex justify-between items-center">
        <span>字典组件展示</span>
        <el-button type="primary" size="small" @click="emit('refresh')">手动刷新</el-button>
      </div>
    </template>

    <div class="dict-component-demo">
      <h4 class="mt-4 mb-3">性别组件</h4>
      <el-radio-group v-model="selectedGender">
        <el-radio v-for="item in dictItems" :key="item.value" :value="item.value">
          {{ item.label }}
        </el-radio>
      </el-radio-group>

      <h4 class="mt-4 mb-3">性别标签</h4>
      <div>
        <el-tag
          v-for="item in dictItems"
          :key="item.value"
          :type="item.tagType || undefined"
          class="mr-2"
        >
          {{ item.label }}
        </el-tag>
      </div>

      <div class="mt-4 pt-3 border-top">
        <div class="text-muted mb-2">已选择值: {{ selectedGender }}</div>
        <div class="text-muted">最后更新: {{ lastUpdateTime }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { DictItemOption } from "@/api/system/dict-items-api";

const selectedGender = defineModel<string>({ required: true });

defineProps<{
  dictItems: DictItemOption[];
  lastUpdateTime: string;
}>();

const emit = defineEmits<{
  refresh: [];
}>();
</script>

<style scoped>
.dict-card {
  display: flex;
  flex-direction: column;
  height: 600px;
  overflow: hidden;
}

.dict-card :deep(.el-card__body) {
  flex: 1;
  overflow: auto;
}

.dict-component-demo {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px;
}

.text-muted {
  font-size: 0.9em;
  color: #909399;
}

.border-top {
  border-top: 1px solid #ebeef5;
}
</style>
