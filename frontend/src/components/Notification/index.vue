<template>
  <el-dropdown trigger="click">
    <button
      type="button"
      class="navbar-icon-button"
      :aria-label="notificationAriaLabel"
      aria-haspopup="menu"
    >
      <el-badge v-if="noticeList.length > 0" :value="noticeList.length" :max="99">
        <AppIcon name="bell" :size="18" />
      </el-badge>

      <AppIcon v-else name="bell" :size="18" />
    </button>

    <template #dropdown>
      <div class="notification-list">
        <div v-if="noticeLoadFailed" class="notification-list__status" role="alert">
          <p>{{ t("navbar.notificationsUnavailable") }}</p>
          <el-button type="primary" link @click="fetchMyNotice">{{ t("common.retry") }}</el-button>
        </div>
        <div
          v-else-if="noticeLoading"
          class="notification-list__status"
          role="status"
          :aria-label="t('navbar.loadingNotifications')"
        >
          <AppIcon name="loader-circle" :size="24" class="is-loading" />
        </div>
        <template v-else-if="noticeList.length > 0">
          <div v-for="item in noticeList" :key="item.id" class="py-3">
            <div class="flex-y-center">
              <DictLabel v-model="item.type" code="notice_type" size="small" />
              <button
                type="button"
                class="notification-list__title"
                :disabled="openingNotice"
                @click="handleReadNotice(item.id)"
              >
                {{ item.title }}
              </button>

              <div class="text-xs text-gray">
                {{ item.publishTime }}
              </div>
            </div>
          </div>
          <el-divider />
          <div class="flex-x-between">
            <el-button type="primary" link @click="handleViewMoreNotice">
              <span class="text-xs">{{ t("navbar.viewMoreNotifications") }}</span>
              <AppIcon name="arrow-right" :size="14" />
            </el-button>
            <el-button
              v-if="noticeList.length > 0"
              type="primary"
              link
              :loading="markingRead"
              @click="handleMarkAllAsRead"
            >
              <span class="text-xs">{{ t("navbar.markAllNotificationsRead") }}</span>
            </el-button>
          </div>
        </template>
        <template v-else>
          <div class="flex-center h-150px">
            <el-empty :image-size="50" :description="t('navbar.noNotifications')" />
          </div>
        </template>
      </div>
    </template>
  </el-dropdown>

  <ProDialog
    v-model="noticeDialogVisible"
    :title="noticeDetail?.title ?? t('navbar.notificationDetail')"
    width="800px"
    class="notification-detail"
    :show-footer="false"
  >
    <div v-if="noticeDetail" class="p-x-20px">
      <div class="flex-y-center mb-16px text-13px text-color-secondary">
        <span class="flex-y-center">
          <AppIcon name="user" :size="14" />
          {{ noticeDetail.publisherName }}
        </span>
        <span class="ml-2 flex-y-center">
          <AppIcon name="activity" :size="14" />
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
import AppIcon from "@/components/AppIcon/index.vue";

interface NotificationMessagePayload {
  id: string;
  title?: string;
  type?: NoticePageVO["type"];
  publishTime?: NoticePageVO["publishTime"];
}

const noticeList = ref<NoticePageVO[]>([]);
const noticeLoading = ref(true);
const noticeLoadFailed = ref(false);
const openingNotice = ref(false);
const markingRead = ref(false);
const noticeDialogVisible = ref(false);
const noticeDetail = ref<NoticeDetailVO | null>(null);
const { t } = useI18n();

const notificationAriaLabel = computed(() =>
  noticeList.value.length > 0
    ? t("navbar.notificationsUnread", { count: noticeList.value.length })
    : t("navbar.notifications")
);

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
            title: t("navbar.newNotification"),
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
async function fetchMyNotice() {
  noticeLoading.value = true;
  noticeLoadFailed.value = false;
  try {
    const data = await NoticeAPI.getMyNoticePage({ pageNum: 1, pageSize: 5, isRead: 0 });
    noticeList.value = data.list;
  } catch {
    noticeLoadFailed.value = true;
  } finally {
    noticeLoading.value = false;
  }
}

// 阅读通知公告
async function handleReadNotice(id: string) {
  if (openingNotice.value) return;
  openingNotice.value = true;
  try {
    const data = await NoticeAPI.getDetail(id);
    noticeDialogVisible.value = true;
    noticeDetail.value = data;
    // 标记为已读
    const index = noticeList.value.findIndex((notice) => notice.id === id);
    if (index >= 0) {
      noticeList.value.splice(index, 1);
    }
  } catch {
    // 请求层已展示失败信息；保留原未读项，允许用户重试。
  } finally {
    openingNotice.value = false;
  }
}

// 查看更多
function handleViewMoreNotice() {
  router.push({ name: "MyNotice" });
}

// 全部已读
async function handleMarkAllAsRead() {
  if (markingRead.value) return;
  markingRead.value = true;
  try {
    await NoticeAPI.readAll();
    noticeList.value = [];
  } catch {
    // 请求层已展示失败信息；未成功时不清空列表。
  } finally {
    markingRead.value = false;
  }
}

onMounted(() => {
  fetchMyNotice();
});

onBeforeUnmount(() => {
  unsubscribe("/user/queue/message");
});
</script>

<style lang="scss" scoped>
.notification-list {
  box-sizing: border-box;
  width: min(460px, calc(100vw - 24px));
  max-height: min(520px, calc(100dvh - 100px));
  padding: 16px;
  overflow-y: auto;
}

.notification-list__title {
  flex: 1;
  min-width: 0;
  padding: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  font: inherit;
  font-size: 13px;
  color: var(--el-text-color-primary);
  text-align: left;
  white-space: nowrap;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 6px;

  &:hover,
  &:focus-visible {
    color: var(--el-color-primary);
    outline: 2px solid var(--el-color-primary);
    outline-offset: -2px;
  }
}

.notification-list__status {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  color: var(--el-text-color-secondary);
}
</style>
