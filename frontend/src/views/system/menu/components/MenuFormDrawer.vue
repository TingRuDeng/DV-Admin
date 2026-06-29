<template>
  <ProFormDrawer
    ref="menuFormRef"
    v-model="dialogState.visible"
    :title="dialogState.title"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    :size="drawerSize"
    label-width="100px"
    class="ff-menu-drawer"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item label="父级菜单" prop="parentId">
      <el-tree-select
        v-model="formData.parentId"
        placeholder="选择上级菜单"
        :data="menuOptions"
        node-key="id"
        filterable
        check-strictly
        :render-after-expand="false"
        class="w-full"
      />
    </el-form-item>

    <el-form-item label="菜单名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入菜单名称" />
    </el-form-item>

    <el-form-item label="菜单类型" prop="type">
      <el-radio-group v-model="formData.type" @change="handleMenuTypeChange">
        <el-radio :value="'CATALOG'">根目录</el-radio>
        <el-radio :value="'MENU'">子菜单</el-radio>
        <el-radio :value="'BUTTON'">按钮</el-radio>
        <el-radio :value="'EXTLINK'">外链</el-radio>
      </el-radio-group>
    </el-form-item>

    <MenuRouteFields :model="formData" />

    <el-form-item v-if="formData.type !== 'BUTTON'" prop="visible" label="显示状态">
      <el-radio-group v-model="formData.visible">
        <el-radio :value="1">显示</el-radio>
        <el-radio :value="0">隐藏</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item v-if="formData.type === 'CATALOG' || formData.type === 'MENU'">
      <template #label>
        <div class="flex items-center">
          始终显示
          <el-tooltip placement="bottom" effect="light">
            <template #content>
              选择"是"，即使目录或菜单下只有一个子节点，也会显示父节点。
              <br />
              选择"否"，如果目录或菜单下只有一个子节点，则只显示该子节点，隐藏父节点。
              <br />
              如果是叶子节点，请选择"否"。
            </template>
            <el-icon class="ml-1 cursor-pointer text-primary">
              <QuestionFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </template>

      <el-radio-group v-model="formData.alwaysShow">
        <el-radio :value="1">是</el-radio>
        <el-radio :value="0">否</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item v-if="formData.type === 'MENU'" label="缓存页面">
      <el-radio-group v-model="formData.keepAlive">
        <el-radio :value="1">开启</el-radio>
        <el-radio :value="0">关闭</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="排序" prop="sort">
      <el-input-number
        v-model="formData.sort"
        style="width: 100px"
        controls-position="right"
        :min="0"
      />
    </el-form-item>

    <el-form-item v-if="formData.type === 'BUTTON'" label="权限标识" prop="perm">
      <el-input v-model="formData.perm" placeholder="sys:user:add" />
    </el-form-item>

    <el-form-item v-if="formData.type !== 'BUTTON'" label="图标" prop="icon">
      <icon-select v-model="formData.icon" />
    </el-form-item>

    <el-form-item v-if="formData.type === 'CATALOG'" label="跳转路由">
      <el-input v-model="formData.redirect" placeholder="跳转路由" />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
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
const menuOptions = ref<OptionType[]>([]);
const initialMenuFormData = ref<MenuForm>(createDefaultMenuForm());
const formData = ref<MenuForm>(createDefaultMenuForm());

const dialogState = reactive({
  title: "新增菜单",
  visible: false,
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const rules: FormRules = {
  parentId: [{ required: true, message: "请选择父级菜单", trigger: "blur" }],
  name: [{ required: true, message: "请输入菜单名称", trigger: "blur" }],
  type: [{ required: true, message: "请选择菜单类型", trigger: "blur" }],
  routeName: [{ required: true, message: "请输入路由名称", trigger: "blur" }],
  routePath: [{ required: true, message: "请输入路由路径", trigger: "blur" }],
  component: [{ required: true, message: "请输入组件路径", trigger: "blur" }],
  visible: [{ required: true, message: "请选择显示状态", trigger: "change" }],
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
  const options = await MenuAPI.getOptions(true);
  menuOptions.value = [{ id: "0", label: "顶级目录", children: options }];
}

async function openCreate(parent?: string) {
  formData.value = {
    ...createDefaultMenuForm(),
    parentId: parent || "0",
  };
  initialMenuFormData.value = { ...formData.value };
  dialogState.title = "新增菜单";
  dialogState.visible = true;
  await loadMenuOptions();
}

async function openEdit(menuId: string) {
  formData.value = createDefaultMenuForm();
  dialogState.title = "编辑菜单";
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
    ElMessage.error("父级菜单不能为当前菜单");
    formLoading.value = false;
    return;
  }

  const request = menuId ? MenuAPI.update(menuId, submitData) : MenuAPI.create(submitData);
  request
    .then(() => {
      ElMessage.success(menuId ? "修改成功" : "新增成功");
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
