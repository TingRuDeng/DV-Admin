<template>
  <ProFormDrawer
    ref="menuFormRef"
    v-model="dialogState.visible"
    :title="t(dialogState.titleKey)"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    :size="drawerSize"
    label-width="100px"
    class="ff-menu-drawer"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item :label="t('system.parentMenu')" prop="parentId">
      <el-tree-select
        v-model="formData.parentId"
        :placeholder="t('system.parentMenuPlaceholder')"
        :data="menuOptions"
        node-key="id"
        filterable
        check-strictly
        :render-after-expand="false"
        class="w-full"
      />
    </el-form-item>

    <el-form-item :label="t('system.menuName')" prop="name">
      <el-input v-model="formData.name" :placeholder="t('system.menuNameRequired')" />
    </el-form-item>

    <el-form-item :label="t('system.menuTypeLabel')" prop="type">
      <el-radio-group v-model="formData.type" @change="handleMenuTypeChange">
        <el-radio :value="'CATALOG'">{{ t("system.rootCatalog") }}</el-radio>
        <el-radio :value="'MENU'">{{ t("system.childMenu") }}</el-radio>
        <el-radio :value="'BUTTON'">{{ t("system.button") }}</el-radio>
        <el-radio :value="'EXTLINK'">{{ t("system.externalLink") }}</el-radio>
      </el-radio-group>
    </el-form-item>

    <MenuRouteFields :model="formData" />

    <el-form-item v-if="formData.type !== 'BUTTON'" prop="visible" :label="t('system.visible')">
      <el-radio-group v-model="formData.visible">
        <el-radio :value="1">{{ t("system.display") }}</el-radio>
        <el-radio :value="0">{{ t("system.hidden") }}</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item
      v-if="formData.type === 'CATALOG' || formData.type === 'MENU'"
      :label="t('system.alwaysVisible')"
    >
      <el-radio-group v-model="formData.alwaysShow">
        <el-radio :value="1">{{ t("common.yes") }}</el-radio>
        <el-radio :value="0">{{ t("common.no") }}</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item v-if="formData.type === 'MENU'" :label="t('system.keepAlive')">
      <el-radio-group v-model="formData.keepAlive">
        <el-radio :value="1">{{ t("system.open") }}</el-radio>
        <el-radio :value="0">{{ t("system.closeState") }}</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item :label="t('common.sort')" prop="sort">
      <el-input-number
        v-model="formData.sort"
        style="width: 100px"
        controls-position="right"
        :min="0"
      />
    </el-form-item>

    <el-form-item v-if="formData.type === 'BUTTON'" :label="t('system.permissionKey')" prop="perm">
      <el-input v-model="formData.perm" placeholder="sys:user:add" />
    </el-form-item>

    <el-form-item v-if="formData.type !== 'BUTTON'" :label="t('system.icon')" prop="icon">
      <icon-select v-model="formData.icon" />
    </el-form-item>

    <el-form-item v-if="formData.type === 'CATALOG'" :label="t('system.redirect')">
      <el-input v-model="formData.redirect" :placeholder="t('system.redirect')" />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import { DeviceEnum } from "@/enums/settings/device-enum";
import { useAppStore } from "@/store/modules/app-store";
import MenuAPI, { type MenuForm } from "@/api/system/menu-api";
import MenuRouteFields from "./MenuRouteFields.vue";

const emit = defineEmits<{
  success: [];
}>();

const appStore = useAppStore();
const menuFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);
const menuChildren = ref<OptionType[]>([]);
const menuOptions = computed(() => [
  { id: "0", label: t("system.topCatalog"), children: menuChildren.value },
]);
const initialMenuFormData = ref<MenuForm>(createDefaultMenuForm());
const formData = ref<MenuForm>(createDefaultMenuForm());

const dialogState = reactive({
  titleKey: "system.addMenu",
  visible: false,
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const rules: FormRules = {
  parentId: [{ required: true, message: () => t("system.parentMenuRequired"), trigger: "blur" }],
  name: [{ required: true, message: () => t("system.menuNameRequired"), trigger: "blur" }],
  type: [{ required: true, message: () => t("system.menuTypeRequired"), trigger: "blur" }],
  routeName: [{ required: true, message: () => t("system.routeNameRequired"), trigger: "blur" }],
  routePath: [{ required: true, message: () => t("system.routePathRequired"), trigger: "blur" }],
  component: [{ required: true, message: () => t("system.componentRequired"), trigger: "blur" }],
  visible: [{ required: true, message: () => t("system.visibleRequired"), trigger: "change" }],
};

function createDefaultMenuForm(): MenuForm {
  return {
    id: undefined,
    parentId: "0",
    visible: 1,
    sort: 1,
    type: "MENU",
    alwaysShow: 0,
    keepAlive: 1,
    params: [],
  };
}

async function loadMenuOptions() {
  menuChildren.value = await MenuAPI.getOptions(true);
}

async function openCreate(parent?: string) {
  formData.value = {
    ...createDefaultMenuForm(),
    parentId: parent || "0",
  };
  initialMenuFormData.value = { ...formData.value };
  dialogState.titleKey = "system.addMenu";
  dialogState.visible = true;
  await loadMenuOptions();
}

async function openEdit(menuId: string) {
  formData.value = createDefaultMenuForm();
  dialogState.titleKey = "system.editMenu";
  dialogState.visible = true;
  await loadMenuOptions();
  const data = await MenuAPI.getFormData(menuId);
  if (data.parentId === null || data.parentId === undefined) {
    data.parentId = "0";
  }
  initialMenuFormData.value = { ...data };
  formData.value = data;
}

function handleMenuTypeChange() {
  if (formData.value.type !== initialMenuFormData.value.type && formData.value.type === "MENU") {
    if (initialMenuFormData.value.type === "CATALOG") {
      formData.value.component = "";
      return;
    }
    formData.value.routePath = initialMenuFormData.value.routePath;
    formData.value.component = initialMenuFormData.value.component;
  }
}

const handleSubmit = useDebounceFn(() => {
  menuFormRef.value?.validate((isValid: boolean) => {
    if (!isValid) {
      formLoading.value = false;
      return;
    }

    submitMenuForm();
  });
}, 300);

function submitMenuForm() {
  const menuId = formData.value.id;
  const submitData = { ...formData.value };

  if (submitData.parentId === "0") {
    delete submitData.parentId;
  }
  if (menuId && submitData.parentId === menuId) {
    ElMessage.error(t("system.currentParentError"));
    formLoading.value = false;
    return;
  }

  const request = menuId ? MenuAPI.update(menuId, submitData) : MenuAPI.create(submitData);
  request
    .then(() => {
      ElMessage.success(menuId ? t("system.updateSuccess") : t("system.createSuccess"));
      handleClose();
      emit("success");
    })
    .finally(() => {
      formLoading.value = false;
    });
}

function handleSubmitWrapper() {
  formLoading.value = true;
  handleSubmit();
}

function handleClose() {
  dialogState.visible = false;
  menuFormRef.value?.resetFields();
  menuFormRef.value?.clearValidate();
  formData.value = createDefaultMenuForm();
  initialMenuFormData.value = createDefaultMenuForm();
}

defineExpose({
  openCreate,
  openEdit,
});
</script>
