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
        <span class="font-semibold text-slate-700">{{ t("system.noticeDetail") }}</span>
        <div class="dialog-toolbar">
          <el-button circle :aria-label="t('system.closeNoticeDetail')" @click="close">
            <template #icon>
              <AppIcon name="close" :size="16" />
            </template>
          </el-button>
        </div>
      </div>
    </template>
    <el-descriptions :column="1">
      <el-descriptions-item :label="t('system.title')">
        {{ currentNotice.title }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('system.publishStatus')">
        <el-tag
          v-if="currentNotice.publishStatus == 0"
          type="info"
          effect="light"
          class="ff-status-tag info"
        >
          {{ t("system.unpublished") }}
        </el-tag>
        <el-tag
          v-else-if="currentNotice.publishStatus == 1"
          type="success"
          effect="light"
          class="ff-status-tag success"
        >
          {{ t("system.publishedStatus") }}
        </el-tag>
        <el-tag
          v-else-if="currentNotice.publishStatus == -1"
          type="warning"
          effect="light"
          class="ff-status-tag warning"
        >
          {{ t("system.revokedStatus") }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item :label="t('system.publisher')">
        {{ currentNotice.publisherName }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('system.releaseTime')">
        {{ currentNotice.publishTime }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('system.noticeContent')">
        <SafeHtml class="ff-notice-content" :content="currentNotice.content" />
      </el-descriptions-item>
    </el-descriptions>
  </ProDialog>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import AppIcon from "@/components/AppIcon/index.vue";
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
