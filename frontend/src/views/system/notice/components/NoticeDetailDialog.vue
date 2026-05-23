<template>
  <ProDialog
    v-model="detailDialog.visible"
    :show-close="false"
    :show-footer="false"
    width="50%"
    append-to-body
    class="ff-notice-detail-dialog"
    @close="close"
  >
    <template #header>
      <div class="flex justify-between items-center">
        <span class="font-semibold text-slate-700">通知公告详情</span>
        <div class="dialog-toolbar">
          <el-button circle @click="close">
            <template #icon>
              <Close />
            </template>
          </el-button>
        </div>
      </div>
    </template>
    <el-descriptions :column="1">
      <el-descriptions-item label="标题：">
        {{ currentNotice.title }}
      </el-descriptions-item>
      <el-descriptions-item label="发布状态：">
        <el-tag
          v-if="currentNotice.publishStatus == 0"
          type="info"
          effect="light"
          class="ff-status-tag info"
        >
          未发布
        </el-tag>
        <el-tag
          v-else-if="currentNotice.publishStatus == 1"
          type="success"
          effect="light"
          class="ff-status-tag success"
        >
          已发布
        </el-tag>
        <el-tag
          v-else-if="currentNotice.publishStatus == -1"
          type="warning"
          effect="light"
          class="ff-status-tag warning"
        >
          已撤回
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="发布人：">
        {{ currentNotice.publisherName }}
      </el-descriptions-item>
      <el-descriptions-item label="发布时间：">
        {{ currentNotice.publishTime }}
      </el-descriptions-item>
      <el-descriptions-item label="公告内容：">
        <SafeHtml class="ff-notice-content" :content="currentNotice.content" />
      </el-descriptions-item>
    </el-descriptions>
  </ProDialog>
</template>

<script setup lang="ts">
import ProDialog from "@/components/ProDialog/index.vue";
import SafeHtml from "@/components/SafeHtml/index.vue";
import NoticeAPI, { type NoticeDetailVO } from "@/api/system/notice-api";

const detailDialog = reactive({
  visible: false,
});
const currentNotice = ref<NoticeDetailVO>({});

function close() {
  detailDialog.visible = false;
}

async function open(id: string) {
  currentNotice.value = await NoticeAPI.getDetail(id);
  detailDialog.visible = true;
}

defineExpose({
  open,
});
</script>
