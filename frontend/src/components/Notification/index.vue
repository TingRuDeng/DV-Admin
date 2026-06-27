<template>
  <el-dropdown trigger="click">
    <el-badge v-if="noticeList.length > 0" :value="noticeList.length" :max="99">
      <div class="i-svg:bell" />
    </el-badge>

    <div v-else class="i-svg:bell" />

    <template #dropdown>
      <div class="p-5">
        <template v-if="noticeList.length > 0">
          <div v-for="(item, index) in noticeList" :key="index" class="w-500px py-3">
            <div class="flex-y-center">
              <DictLabel v-model="item.type" code="notice_type" size="small" />
              <el-text
                size="small"
                class="w-200px cursor-pointer !ml-2 !flex-1"
                truncated
                @click="handleReadNotice(item.id)"
              >
                {{ item.title }}
              </el-text>

              <div class="text-xs text-gray">
                {{ item.publishTime }}
              </div>
            </div>
          </div>
          <el-divider />
          <div class="flex-x-between">
            <el-link type="primary" underline="never" @click="handleViewMoreNotice">
              <span class="text-xs">查看更多</span>
              <el-icon class="text-xs">
                <ArrowRight />
              </el-icon>
            </el-link>
            <el-link
              v-if="noticeList.length > 0"
              type="primary"
              underline="never"
              @click="handleMarkAllAsRead"
            >
              <span class="text-xs">全部已读</span>
            </el-link>
          </div>
        </template>
        <template v-else>
          <div class="flex-center h-150px w-350px">
            <el-empty :image-size="50" description="暂无消息" />
          </div>
        </template>
      </div>
    </template>
  </el-dropdown>

  <ProDialog
    v-model="noticeDialogVisible"
    :title="noticeDetail?.title ?? '通知详情'"
    width="800px"
    class="notification-detail"
    :show-footer="false"
  >
    <div v-if="noticeDetail" class="p-x-20px">
      <div class="flex-y-center mb-16px text-13px text-color-secondary">
        <span class="flex-y-center">
          <el-icon><User /></el-icon>
          {{ noticeDetail.publisherName }}
        </span>
        <span class="ml-2 flex-y-center">
          <el-icon><Timer /></el-icon>
          {{ noticeDetail.publishTime }}
        </span>
      </div>

      <div class="max-h-60vh pt-16px mb-24px overflow-y-auto border-t border-solid border-color">
        <SafeHtml :content="noticeDetail.content" />
      </div>
    </div>
  </ProDialog>
</template>

<script setup lang="ts">
import type { IMessage } from "@stomp/stompjs";

import ProDialog from "@/components/ProDialog/index.vue";
import SafeHtml from "@/components/SafeHtml/index.vue";
import NoticeAPI, { NoticePageVO, NoticeDetailVO } from "@/api/system/notice-api";
import router from "@/router";
import { useStomp } from "@/composables/websocket/useStomp";

interface NotificationMessagePayload {
  id: string;
  title?: string;
  type?: NoticePageVO["type"];
  publishTime?: NoticePageVO["publishTime"];
}

const noticeList = ref<NoticePageVO[]>([]);
const noticeDialogVisible = ref(false);
const noticeDetail = ref<NoticeDetailVO | null>(null);

const { subscribe, unsubscribe, isConnected } = useStomp();

watch(
  () => isConnected.value,
  (connected) => {
    if (connected) {
      subscribe("/user/queue/message", (message: IMessage) => {
        const data = parseNotificationMessage(message);
        const id = data.id;
        if (!noticeList.value.some((notice) => notice.id === id)) {
          noticeList.value.unshift({
            id,
            title: data.title,
            type: data.type,
            publishTime: data.publishTime,
          });

          ElNotification({
            title: "您收到一条新的通知消息！",
            message: data.title ?? "",
            type: "success",
            position: "bottom-right",
          });
        }
      });
    }
  }
);

function parseNotificationMessage(message: IMessage): NotificationMessagePayload {
  const data: unknown = JSON.parse(message.body);
  return toNotificationMessagePayload(data);
}

function toNotificationMessagePayload(data: unknown): NotificationMessagePayload {
  if (!isNotificationMessageRecord(data)) {
    throw new Error("通知消息格式错误");
  }

  return {
    id: String(data.id),
    title: normalizeOptionalString(data.title),
    type: normalizeNoticeType(data.type),
    publishTime: normalizePublishTime(data.publishTime),
  };
}

function isNotificationMessageRecord(
  data: unknown
): data is Record<string, unknown> & { id: string | number } {
  return isRecord(data) && (typeof data.id === "string" || typeof data.id === "number");
}

function isRecord(data: unknown): data is Record<string, unknown> {
  return typeof data === "object" && data !== null;
}

function normalizeOptionalString(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function normalizeNoticeType(value: unknown): NoticePageVO["type"] {
  return typeof value === "number" ? value : undefined;
}

function normalizePublishTime(value: unknown): NoticePageVO["publishTime"] {
  if (typeof value === "string" || value instanceof Date) {
    return value;
  }
  return undefined;
}

/**
 * 获取我的通知公告
 */
function featchMyNotice() {
  NoticeAPI.getMyNoticePage({ pageNum: 1, pageSize: 5, isRead: 0 }).then((data) => {
    noticeList.value = data.list;
  });
}

// 阅读通知公告
function handleReadNotice(id: string) {
  NoticeAPI.getDetail(id).then((data) => {
    noticeDialogVisible.value = true;
    noticeDetail.value = data;
    // 标记为已读
    const index = noticeList.value.findIndex((notice) => notice.id === id);
    if (index >= 0) {
      noticeList.value.splice(index, 1);
    }
  });
}

// 查看更多
function handleViewMoreNotice() {
  router.push({ name: "MyNotice" });
}

// 全部已读
function handleMarkAllAsRead() {
  NoticeAPI.readAll().then(() => {
    noticeList.value = [];
  });
}

onMounted(() => {
  featchMyNotice();
});

onBeforeUnmount(() => {
  unsubscribe("/user/queue/message");
});
</script>

<style lang="scss" scoped></style>
