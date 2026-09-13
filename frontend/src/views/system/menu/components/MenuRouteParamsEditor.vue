<template>
  <div v-if="!params || params.length === 0">
    <el-button
      type="success"
      plain
      class="ff-button-success"
      @click="params = [{ key: '', value: '' }]"
    >
      {{ t("system.addRouteParam") }}
    </el-button>
  </div>

  <div v-else>
    <div v-for="(item, index) in params" :key="index" class="flex items-center gap-2 mb-2">
      <el-input v-model="item.key" :placeholder="t('system.paramName')" style="width: 100px" />

      <span class="text-slate-400">=</span>

      <el-input v-model="item.value" :placeholder="t('system.paramValue')" style="width: 100px" />

      <button
        v-if="params.indexOf(item) === params.length - 1"
        type="button"
        class="route-param-action text-success"
        :aria-label="t('system.addRouteParam')"
        @click="params.push({ key: '', value: '' })"
      >
        <AppIcon name="plus" :size="18" />
      </button>
      <button
        type="button"
        class="route-param-action text-danger"
        :aria-label="t('system.removeRouteParam')"
        @click="params.splice(params.indexOf(item), 1)"
      >
        <AppIcon name="delete" :size="18" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import AppIcon from "@/components/AppIcon/index.vue";
type MenuRouteParam = {
  key: string;
  value: string;
};

const params = defineModel<MenuRouteParam[] | undefined>({ required: true });
</script>

<style scoped>
.route-param-action {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  padding: 2px;
  cursor: pointer;
  background: transparent;
  border: 0;
}
</style>
