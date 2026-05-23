<template>
  <el-card shadow="hover" class="dict-card">
    <template #header>
      <div class="flex justify-between items-center">
        <span>字典缓存数据</span>
        <div>
          <el-tag v-if="cached" type="success" class="ml-2" size="small">已缓存</el-tag>
          <el-tag v-else type="danger" class="ml-2" size="small">未缓存</el-tag>
        </div>
      </div>
    </template>

    <div class="cache-content">
      <pre class="cache-data">{{ formattedCache }}</pre>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { DictItemOption } from "@/api/system/dict-items-api";

const props = defineProps<{
  cached: boolean;
  dictItems: DictItemOption[];
}>();

const formattedCache = computed(() => JSON.stringify(props.dictItems, null, 2));
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

.cache-content {
  height: 100%;
  overflow: hidden;
}

.cache-data {
  height: 100%;
  padding: 8px;
  overflow-y: auto;
  font-size: 12px;
  word-wrap: break-word;
  white-space: pre-wrap;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
