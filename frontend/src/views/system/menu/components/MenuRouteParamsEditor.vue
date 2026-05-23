<template>
  <div v-if="!params || params.length === 0">
    <el-button
      type="success"
      plain
      class="ff-button-success"
      @click="params = [{ key: '', value: '' }]"
    >
      添加路由参数
    </el-button>
  </div>

  <div v-else>
    <div v-for="(item, index) in params" :key="index" class="flex items-center gap-2 mb-2">
      <el-input v-model="item.key" placeholder="参数名" style="width: 100px" />

      <span class="text-slate-400">=</span>

      <el-input v-model="item.value" placeholder="参数值" style="width: 100px" />

      <el-icon
        v-if="params.indexOf(item) === params.length - 1"
        class="cursor-pointer text-success"
        style="vertical-align: -0.15em"
        @click="params.push({ key: '', value: '' })"
      >
        <CirclePlusFilled />
      </el-icon>
      <el-icon
        class="cursor-pointer text-danger"
        style="vertical-align: -0.15em"
        @click="params.splice(params.indexOf(item), 1)"
      >
        <DeleteFilled />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
type MenuRouteParam = {
  key: string;
  value: string;
};

const params = defineModel<MenuRouteParam[] | undefined>({ required: true });
</script>
