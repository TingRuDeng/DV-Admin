<!-- 部门树 -->
<template>
  <el-card shadow="never">
    <el-input v-model="deptName" placeholder="部门名称" clearable>
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>

    <el-tree
      ref="deptTreeRef"
      class="mt-2"
      :data="deptList"
      :props="{ children: 'children', label: 'label', disabled: '' }"
      :expand-on-click-node="false"
      :filter-node-method="handleFilter"
      default-expand-all
      @node-click="handleNodeClick"
    />
  </el-card>
</template>

<script setup lang="ts">
import DeptAPI from "@/api/system/dept-api";
import type { TreeInstance } from "element-plus";

const props = defineProps<{
  modelValue?: string | number;
}>();

const deptList = ref<OptionType[]>(); // 部门列表
const deptTreeRef = ref<TreeInstance | null>(null); // 部门树
const deptName = ref(""); // 部门名称

const emits = defineEmits<{
  "node-click": [];
  "update:modelValue": [value?: string | number];
}>();

const deptId = useVModel(props, "modelValue", emits);

watchEffect(
  () => {
    deptTreeRef.value?.filter(deptName.value);
  },
  {
    flush: "post", // watchEffect会在DOM挂载或者更新之前就会触发，此属性控制在DOM元素更新后运行
  }
);

/**
 * 部门筛选
 */
function handleFilter(value: string, data: { label?: string }) {
  if (!value) {
    return true;
  }
  return data.label?.includes(value) ?? false;
}

/** 部门树节点 Click */
function handleNodeClick(data: OptionType) {
  deptId.value = data.id;
  emits("node-click");
}

onBeforeMount(() => {
  DeptAPI.getOptions().then((data) => {
    deptList.value = data;
  });
});
</script>
