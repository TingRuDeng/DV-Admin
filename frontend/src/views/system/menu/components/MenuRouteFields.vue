<template>
  <el-form-item v-if="model.type === 'EXTLINK'" label="外链地址" prop="path">
    <el-input v-model="model.routePath" placeholder="请输入外链完整路径" />
  </el-form-item>

  <el-form-item v-if="model.type === 'MENU'" prop="routeName">
    <template #label>
      <div class="flex items-center">
        路由名称
        <el-tooltip placement="bottom" effect="light">
          <template #content>
            如果需要开启缓存，需保证页面 defineOptions 中的 name 与此处一致，建议使用驼峰。
          </template>
          <el-icon class="ml-1 cursor-pointer text-primary">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </template>
    <el-input v-model="model.routeName" placeholder="User" />
  </el-form-item>

  <el-form-item v-if="model.type === 'CATALOG' || model.type === 'MENU'" prop="routePath">
    <template #label>
      <div class="flex items-center">
        路由路径
        <el-tooltip placement="bottom" effect="light">
          <template #content>
            定义应用中不同页面对应的 URL 路径，目录需以 / 开头，菜单项不用。例如：系统管理目录
            /system，系统管理下的用户管理菜单 user。
          </template>
          <el-icon class="ml-1 cursor-pointer text-primary">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </template>
    <el-input v-if="model.type === 'CATALOG'" v-model="model.routePath" placeholder="system" />
    <el-input v-else v-model="model.routePath" placeholder="user" />
  </el-form-item>

  <el-form-item v-if="model.type === 'MENU'" prop="component">
    <template #label>
      <div class="flex items-center">
        组件路径
        <el-tooltip placement="bottom" effect="light">
          <template #content>
            组件页面完整路径，相对于 src/views/，如 system/user/index，缺省后缀 .vue
          </template>
          <el-icon class="ml-1 cursor-pointer text-primary">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </template>

    <el-input v-model="model.component" placeholder="system/user/index">
      <template #prepend>src/views/</template>
      <template #append>.vue</template>
    </el-input>
  </el-form-item>

  <el-form-item v-if="model.type === 'MENU'">
    <template #label>
      <div class="flex items-center">
        路由参数
        <el-tooltip placement="bottom" effect="light">
          <template #content>组件页面使用 `useRoute().query.参数名` 获取路由参数值。</template>
          <el-icon class="ml-1 cursor-pointer text-primary">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </template>

    <MenuRouteParamsEditor v-model="model.params" />
  </el-form-item>
</template>

<script setup lang="ts">
import type { MenuForm } from "@/api/system/menu-api";
import MenuRouteParamsEditor from "./MenuRouteParamsEditor.vue";

defineProps<{
  model: MenuForm;
}>();
</script>
