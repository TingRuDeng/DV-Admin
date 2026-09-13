<template>
  <ProFormDrawer
    ref="deptFormRef"
    v-model="visible"
    :title="title"
    :model="drawerModel"
    :rules="rules"
    :loading="loading"
    size="600px"
    label-width="80px"
    @submit="emit('submit')"
    @close="emit('close')"
  >
    <el-form-item :label="t('system.parentDept')" prop="parentId">
      <el-tree-select
        v-model="model.parentId"
        :placeholder="t('system.parentDeptPlaceholder')"
        :data="deptOptions"
        filterable
        node-key="id"
        check-strictly
        :render-after-expand="false"
        class="w-full"
      />
    </el-form-item>

    <el-form-item :label="t('system.deptName')" prop="name">
      <el-input v-model="model.name" :placeholder="t('system.deptNamePlaceholder')" />
    </el-form-item>

    <el-form-item :label="t('system.displaySort')" prop="sort">
      <el-input-number
        v-model="model.sort"
        controls-position="right"
        style="width: 120px"
        :min="0"
      />
    </el-form-item>

    <el-form-item :label="t('system.status')">
      <el-radio-group v-model="model.status">
        <el-radio :value="1">{{ t("common.normal") }}</el-radio>
        <el-radio :value="0">{{ t("common.disabled") }}</el-radio>
      </el-radio-group>
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { FormInstance, FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import type { DeptForm } from "@/api/system/dept-api";

const visible = defineModel<boolean>({ required: true });

const props = defineProps<{
  title: string;
  model: DeptForm;
  rules: FormRules<DeptForm>;
  loading: boolean;
  deptOptions: OptionType[];
}>();

const emit = defineEmits<{
  submit: [];
  close: [];
}>();

const deptFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const drawerModel = computed(() => props.model as Record<string, unknown>);

defineExpose({
  resetFields: () => deptFormRef.value?.resetFields(),
  clearValidate: () => deptFormRef.value?.clearValidate(),
  validate: (callback?: Parameters<FormInstance["validate"]>[0]) =>
    deptFormRef.value?.validate(callback),
});
</script>
