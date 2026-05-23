<template>
  <el-card shadow="hover" class="dict-card">
    <template #header>
      <div class="flex justify-between items-center">
        <span>性别字典项 - 男</span>
        <el-button type="warning" size="small" @click="emit('reload')">重新加载</el-button>
      </div>
    </template>

    <div>
      <div v-if="model" class="dict-form">
        <el-form :model="model" label-width="80px">
          <el-form-item label="字典编码">
            <el-input v-model="model.dictCode" disabled />
          </el-form-item>
          <el-form-item label="字典标签">
            <el-input v-model="model.label" />
          </el-form-item>
          <el-form-item label="字典值">
            <el-input v-model="model.value" disabled />
          </el-form-item>
          <el-form-item label="标记颜色">
            <el-select v-model="model.tagType" placeholder="选择标签类型" style="width: 100%">
              <el-option value="success" label="success">
                <el-tag type="success">success</el-tag>
              </el-option>
              <el-option value="warning" label="warning">
                <el-tag type="warning">warning</el-tag>
              </el-option>
              <el-option value="danger" label="danger">
                <el-tag type="danger">danger</el-tag>
              </el-option>
              <el-option value="info" label="info">
                <el-tag type="info">info</el-tag>
              </el-option>
              <el-option value="primary" label="primary">
                <el-tag type="primary">primary</el-tag>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="emit('save')">保存</el-button>
            <el-button @click="emit('reload')">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      <el-empty v-else description="暂无字典数据" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { DictItemForm } from "@/api/system/dict-items-api";

defineProps<{
  model: DictItemForm | null;
  saving: boolean;
}>();

const emit = defineEmits<{
  reload: [];
  save: [];
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

.dict-form {
  margin-bottom: 20px;
}
</style>
