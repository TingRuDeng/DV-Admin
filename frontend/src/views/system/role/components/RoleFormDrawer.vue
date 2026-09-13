<template>
  <ProFormDrawer
    ref="roleFormRef"
    v-model="dialogState.visible"
    :title="t(dialogState.titleKey)"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    :size="drawerSize"
    label-width="100px"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item :label="t('system.roleName')" prop="name">
      <el-input v-model="formData.name" :placeholder="t('system.roleNameRequired')" />
    </el-form-item>
    <el-form-item :label="t('common.status')" prop="status">
      <el-radio-group v-model="formData.status">
        <el-radio :value="1">{{ t("common.normal") }}</el-radio>
        <el-radio :value="0">{{ t("system.stop") }}</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item :label="t('system.default')" prop="isDefault">
      <el-radio-group v-model="formData.isDefault">
        <el-radio :value="1">{{ t("common.yes") }}</el-radio>
        <el-radio :value="0">{{ t("common.no") }}</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item :label="t('system.dataPermission')" prop="dataScope">
      <el-select
        v-model="formData.dataScope"
        :placeholder="t('system.dataPermissionPlaceholder')"
        class="w-full"
      >
        <el-option
          v-for="item in dataScopeOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </el-form-item>
    <el-form-item
      v-if="formData.dataScope === DATA_SCOPE_CUSTOM"
      :label="t('system.permissionDept')"
      prop="deptIds"
    >
      <el-tree-select
        v-model="formData.deptIds"
        :placeholder="t('system.permissionDeptPlaceholder')"
        :data="deptOptions"
        node-key="id"
        multiple
        filterable
        check-strictly
        :render-after-expand="false"
        class="w-full"
      />
    </el-form-item>
    <el-form-item :label="t('common.sort')" prop="sort">
      <el-input-number
        v-model="formData.sort"
        controls-position="right"
        :min="0"
        style="width: 100px"
      />
    </el-form-item>
    <el-form-item :label="t('system.roleRemark')" prop="desc">
      <el-input
        v-model="formData.desc"
        :placeholder="t('system.roleRemarkPlaceholder')"
        type="textarea"
        :rows="2"
      />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { FormRules } from "element-plus";
import DeptAPI from "@/api/system/dept-api";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import { DeviceEnum } from "@/enums/settings/device-enum";
import RoleAPI, { type RoleForm } from "@/api/system/role-api";
import { useAppStore } from "@/store/modules/app-store";

const emit = defineEmits<{
  success: [];
}>();

const appStore = useAppStore();
const roleFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);
const deptOptions = ref<OptionType[]>();

const DATA_SCOPE_ALL = 1;
const DATA_SCOPE_SELF = 2;
const DATA_SCOPE_DEPT = 3;
const DATA_SCOPE_DEPT_AND_CHILDREN = 4;
const DATA_SCOPE_CUSTOM = 5;

const dataScopeOptions = computed(() => [
  { label: t("system.allData"), value: DATA_SCOPE_ALL },
  { label: t("system.selfData"), value: DATA_SCOPE_SELF },
  { label: t("system.deptDataScope"), value: DATA_SCOPE_DEPT },
  { label: t("system.deptChildrenData"), value: DATA_SCOPE_DEPT_AND_CHILDREN },
  { label: t("system.customDeptData"), value: DATA_SCOPE_CUSTOM },
]);

const dialogState = reactive({
  titleKey: "system.addRole",
  visible: false,
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const formData = reactive<RoleForm>({
  sort: 1,
  status: 1,
  isDefault: 1,
  dataScope: DATA_SCOPE_ALL,
  deptIds: [],
});

const rules: FormRules = {
  name: [{ required: true, message: () => t("system.roleNameRequired"), trigger: "blur" }],
  status: [{ required: true, message: () => t("system.statusRequired"), trigger: "blur" }],
  dataScope: [
    { required: true, message: () => t("system.dataPermissionPlaceholder"), trigger: "change" },
  ],
};

function resetFormData() {
  Object.assign(formData, {
    id: undefined,
    name: undefined,
    sort: 1,
    status: 1,
    isDefault: 1,
    dataScope: DATA_SCOPE_ALL,
    deptIds: [],
    desc: undefined,
  });
}

async function loadOptions() {
  deptOptions.value = await DeptAPI.getOptions();
}

async function openCreate() {
  resetFormData();
  dialogState.titleKey = "system.addRole";
  dialogState.visible = true;
  await loadOptions();
}

async function openEdit(roleId: string) {
  resetFormData();
  dialogState.titleKey = "system.editRole";
  dialogState.visible = true;
  await loadOptions();
  const data = await RoleAPI.getFormData(roleId);
  Object.assign(formData, data);
}

function handleClose() {
  dialogState.visible = false;
  roleFormRef.value?.resetFields();
  roleFormRef.value?.clearValidate();
  resetFormData();
}

const handleSubmit = useDebounceFn(() => {
  roleFormRef.value?.validate((valid: boolean) => {
    if (!valid) {
      formLoading.value = false;
      return;
    }

    const roleId = formData.id;
    const payload: RoleForm = {
      ...toRaw(formData),
      deptIds: formData.dataScope === DATA_SCOPE_CUSTOM ? (formData.deptIds ?? []) : [],
    };
    const request = roleId ? RoleAPI.update(roleId, payload) : RoleAPI.create(payload);
    request
      .then(() => {
        ElMessage.success(roleId ? t("system.updateSuccess") : t("system.createSuccess"));
        handleClose();
        emit("success");
      })
      .finally(() => {
        formLoading.value = false;
      });
  });
}, 300);

function handleSubmitWrapper() {
  formLoading.value = true;
  handleSubmit();
}

defineExpose({
  openCreate,
  openEdit,
});
</script>
