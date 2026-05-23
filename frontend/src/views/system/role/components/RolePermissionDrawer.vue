<template>
  <ProDrawer
    v-model="visible"
    :title="drawerTitle"
    :size="drawerSize"
    :loading="drawerLoading"
    @submit="handleSubmit"
  >
    <div class="flex justify-between items-center mb-5">
      <el-input v-model="permKeywords" clearable class="w-[150px]" placeholder="菜单权限名称">
        <template #prefix>
          <Search />
        </template>
      </el-input>

      <div class="flex items-center gap-3">
        <el-button
          type="primary"
          size="small"
          plain
          class="ff-button-primary"
          @click="togglePermTree"
        >
          <template #icon>
            <Switch />
          </template>
          {{ isExpanded ? "收缩" : "展开" }}
        </el-button>
        <el-checkbox v-model="parentChildLinked" @change="handleParentChildLinkedChange">
          父子联动
        </el-checkbox>
        <el-tooltip placement="bottom">
          <template #content>
            如果只需勾选菜单权限，不需要勾选子菜单或者按钮权限，请关闭父子联动
          </template>
          <el-icon class="text-primary cursor-pointer">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <el-tree
      ref="permTreeRef"
      node-key="id"
      show-checkbox
      :data="menuPermOptions"
      :filter-node-method="handlePermFilter"
      :default-expand-all="true"
      :check-strictly="!parentChildLinked"
      class="permission-tree"
    >
      <template #default="{ data }">
        {{ data.label }}
      </template>
    </el-tree>
    <template #footer="{ cancel, submit }">
      <div class="dialog-footer flex justify-end gap-2">
        <el-button class="ff-button-secondary" @click="cancel">取 消</el-button>
        <el-button type="primary" class="ff-button-primary" @click="submit">确 定</el-button>
      </div>
    </template>
  </ProDrawer>
</template>

<script setup lang="ts">
import type { CheckboxValueType, TreeInstance } from "element-plus";
import ProDrawer from "@/components/ProDrawer/index.vue";
import { DeviceEnum } from "@/enums/settings/device-enum";
import MenuAPI from "@/api/system/menu-api";
import RoleAPI, { type RolePageVO } from "@/api/system/role-api";
import { useAppStore } from "@/store/modules/app-store";

const emit = defineEmits<{
  success: [];
}>();

interface CheckedRole {
  id?: string;
  name?: string;
}

type ExpandableTreeNode = {
  expand: () => void;
  collapse: () => void;
};

type TreeWithNodeMap = TreeInstance & {
  store: {
    nodesMap: Record<string, ExpandableTreeNode>;
  };
};

type CheckedPermNode = OptionType & { id: string | number };

const appStore = useAppStore();
const visible = ref(false);
const drawerLoading = ref(false);
const checkedRole = ref<CheckedRole>({});
const permTreeRef = ref<TreeInstance | null>(null);
const menuPermOptions = ref<OptionType[]>([]);
const permKeywords = ref("");
const isExpanded = ref(true);
const parentChildLinked = ref(true);

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));
const drawerTitle = computed(() => `【${checkedRole.value.name ?? ""}】权限分配`);

async function open(row: RolePageVO) {
  if (!row.id) return;

  visible.value = true;
  drawerLoading.value = true;
  checkedRole.value = {
    id: row.id,
    name: row.name,
  };

  try {
    menuPermOptions.value = await MenuAPI.getOptions();
    const menuIds = await RoleAPI.getRoleMenuIds(row.id);
    menuIds.forEach((menuId) => permTreeRef.value?.setChecked(menuId, true, false));
  } finally {
    drawerLoading.value = false;
  }
}

function handleSubmit() {
  const roleId = checkedRole.value.id;
  if (!roleId) return;

  const checkedMenuIds =
    permTreeRef.value
      ?.getCheckedNodes(false, true)
      .map((node) => Number((node as CheckedPermNode).id))
      .filter((id) => !Number.isNaN(id)) ?? [];

  drawerLoading.value = true;
  RoleAPI.updateRoleMenus(roleId, checkedMenuIds)
    .then(() => {
      ElMessage.success("分配权限成功");
      visible.value = false;
      emit("success");
    })
    .finally(() => {
      drawerLoading.value = false;
    });
}

function togglePermTree() {
  isExpanded.value = !isExpanded.value;
  const nodesMap = (permTreeRef.value as TreeWithNodeMap | null)?.store.nodesMap;
  if (!nodesMap) return;

  Object.values(nodesMap).forEach((node) => {
    if (isExpanded.value) {
      node.expand();
      return;
    }
    node.collapse();
  });
}

watch(permKeywords, (value) => {
  permTreeRef.value?.filter(value);
});

function handlePermFilter(value: string, data: { label?: string }) {
  if (!value) return true;
  return data.label?.includes(value) ?? false;
}

function handleParentChildLinkedChange(value: CheckboxValueType) {
  parentChildLinked.value = Boolean(value);
}

defineExpose({
  open,
});
</script>
