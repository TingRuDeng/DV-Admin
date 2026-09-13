<template>
  <el-form-item
    v-if="model.type === 'EXTLINK'"
    :label="t('system.externalLinkAddress')"
    prop="path"
  >
    <el-input v-model="model.routePath" :placeholder="t('system.externalLinkPlaceholder')" />
  </el-form-item>

  <el-form-item v-if="model.type === 'MENU'" prop="routeName" :label="t('system.routeName')">
    <el-input v-model="model.routeName" placeholder="User" />
  </el-form-item>

  <el-form-item
    v-if="model.type === 'CATALOG' || model.type === 'MENU'"
    prop="routePath"
    :label="t('system.routePath')"
  >
    <el-input v-if="model.type === 'CATALOG'" v-model="model.routePath" placeholder="system" />
    <el-input v-else v-model="model.routePath" placeholder="user" />
  </el-form-item>

  <el-form-item v-if="model.type === 'MENU'" prop="component" :label="t('system.componentPath')">
    <el-input v-model="model.component" placeholder="system/user/index">
      <template #prepend>src/views/</template>
      <template #append>.vue</template>
    </el-input>
  </el-form-item>

  <el-form-item v-if="model.type === 'MENU'" :label="t('system.routeParams')">
    <MenuRouteParamsEditor v-model="model.params" />
  </el-form-item>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { MenuForm } from "@/api/system/menu-api";
import MenuRouteParamsEditor from "./MenuRouteParamsEditor.vue";

defineProps<{
  model: MenuForm;
}>();
</script>
