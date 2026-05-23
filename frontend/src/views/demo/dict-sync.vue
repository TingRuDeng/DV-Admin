<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>字典WebSocket实时更新演示</span>
          <el-tag :type="wsConnected ? 'success' : 'danger'" size="small" class="ml-2">
            WebSocket {{ wsStatusText }}
          </el-tag>
        </div>
      </template>

      <el-alert type="info" :closable="false" class="mb-4">
        本示例展示WebSocket实时更新字典缓存的效果。您可以编辑"男"性别字典项，保存后后端将通过WebSocket通知所有客户端刷新缓存。
      </el-alert>

      <el-row :gutter="16">
        <el-col :span="8">
          <DictItemEditorCard
            :model="dictForm"
            :saving="saving"
            @reload="loadMaleDict"
            @save="saveDict"
          />
        </el-col>

        <el-col :span="8">
          <DictPreviewCard
            v-model="selectedGender"
            :dict-items="dictItems"
            :last-update-time="lastUpdateTime"
            @refresh="refreshDictComponent"
          />
        </el-col>

        <el-col :span="8">
          <DictCacheCard :cached="dictCacheStatus" :dict-items="dictItems" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useDictStoreHook } from "@/store/modules/dict-store";
import { useDateFormat } from "@vueuse/core";
import { DictItemForm } from "@/api/system/dict-items-api";
import { useDictSync, DictMessage } from "@/composables";
import DictItemsApi from "@/api/system/dict-items-api";
import { createLogger } from "@/utils/logger";
import DictCacheCard from "./components/dict-sync/DictCacheCard.vue";
import DictItemEditorCard from "./components/dict-sync/DictItemEditorCard.vue";
import DictPreviewCard from "./components/dict-sync/DictPreviewCard.vue";

const dictSyncDemoLogger = createLogger("DictSyncDemo");

// 性别字典编码
const DICT_CODE = "gender";
// 男性字典项ID
const MALE_ITEM_ID = 1;

// 字典store
const dictStore = useDictStoreHook();
// 保存状态
const saving = ref(false);
// 最后更新时间
const lastUpdateTime = ref("-");
// 字典表单数据
const dictForm = ref<DictItemForm | null>(null);
// 选中的性别
const selectedGender = ref("");

// 初始化WebSocket
const dictWebSocket = useDictSync();

// 获取连接状态
const wsConnected = computed(() => dictWebSocket.isConnected);

// WebSocket连接状态显示文本
const wsStatusText = computed(() => (wsConnected.value ? "已连接" : "未连接"));

// 保存WebSocket清理函数
let unregisterCallback: (() => void) | null = null;

const dictItems = computed(() => dictStore.getDictItems(DICT_CODE));

// 当前选中字典的缓存状态
const dictCacheStatus = computed(() => {
  // 检查字典是否在缓存中
  return dictItems.value.length > 0;
});

// 设置WebSocket
const setupWebSocket = () => {
  // 初始化WebSocket连接
  dictWebSocket.initWebSocket();

  // 注册字典消息回调
  unregisterCallback = dictWebSocket.onDictMessage((message: DictMessage) => {
    // 只有当消息是关于性别字典的更新时才处理
    if (message.dictCode === DICT_CODE) {
      // 更新最后更新时间
      lastUpdateTime.value = useDateFormat(new Date(), "YYYY-MM-DD HH:mm:ss").value;

      // 触发字典组件重新加载
      nextTick(() => {
        refreshDictComponent();
      });
    }
  });
};

// 刷新字典组件，强制重新加载字典数据
const refreshDictComponent = async () => {
  // 这里重新获取字典数据以触发按需加载
  await dictStore.loadDictItems(DICT_CODE);
  ElMessage.success("字典组件已刷新");
};

// 加载男性字典表单数据
const loadMaleDict = async () => {
  // 获取男性字典项表单数据 - 使用接口 /dicts/gender/items/1/form
  const data = await DictItemsApi.getDictItemFormData(MALE_ITEM_ID);
  dictForm.value = data;
};

// 保存字典项
const saveDict = async () => {
  if (!dictForm.value) return;

  saving.value = true;
  try {
    // dictForm的类型已经是DictItemForm，直接传入
    await DictItemsApi.updateDictItem(MALE_ITEM_ID, dictForm.value);

    // 更新时间
    lastUpdateTime.value = useDateFormat(new Date(), "YYYY-MM-DD HH:mm:ss").value;

    ElMessage.success("保存成功，后端将通过WebSocket通知所有客户端");
  } catch (error) {
    dictSyncDemoLogger.error("保存字典项失败:", error);
    ElMessage.error("保存失败");
  } finally {
    saving.value = false;
  }
};

// 组件挂载时加载性别字典
onMounted(async () => {
  await loadMaleDict();
  // 加载初始字典数据
  await dictStore.loadDictItems(DICT_CODE);
  // 初始化选中性别为男
  selectedGender.value = "1";
  // 设置WebSocket
  setupWebSocket();
});

// 组件卸载时清理WebSocket
onUnmounted(() => {
  unregisterCallback?.();
});
</script>
