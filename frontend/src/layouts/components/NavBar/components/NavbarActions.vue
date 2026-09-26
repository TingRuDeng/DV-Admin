<template>
  <div :class="['navbar-actions', navbarActionsClass]">
    <!-- 桌面端工具项 -->
    <template v-if="isDesktop">
      <!-- 搜索：输入框本身可点击，不套 __item 的指针光标和悬停底色 -->
      <div class="navbar-actions__search">
        <MenuSearch />
      </div>

      <!-- 主题切换 -->
      <div class="navbar-actions__item">
        <ThemeToggle />
      </div>

      <!-- 全屏 -->
      <div class="navbar-actions__item">
        <Fullscreen />
      </div>

      <!-- 布局大小 -->
      <div class="navbar-actions__item">
        <SizeSelect />
      </div>

      <!-- 语言选择 -->
      <div class="navbar-actions__item">
        <LangSelect />
      </div>

      <!-- 通知 -->
      <div class="navbar-actions__item">
        <Notification />
      </div>
    </template>

    <!-- 用户菜单 -->
    <div class="navbar-actions__item">
      <el-dropdown trigger="click">
        <button type="button" class="user-profile" :aria-label="t('navbar.userMenu')">
          <img
            v-if="avatarUrl && !avatarLoadFailed"
            class="user-profile__avatar"
            :src="avatarUrl"
            alt=""
            aria-hidden="true"
            @error="avatarLoadFailed = true"
          />
          <!-- 没有头像或加载失败时只显示金属球，不露出浏览器的破图标记 -->
          <span v-else class="user-profile__avatar" aria-hidden="true" />
          <span class="user-profile__name">{{ userStore.userInfo.username }}</span>
        </button>
        <template #dropdown>
          <el-dropdown-menu class="user-menu">
            <!-- 用户卡片只做展示，不是菜单项，不会被键盘选中 -->
            <div class="user-menu__card" :aria-label="t('navbar.userCard')" role="group">
              <img
                v-if="avatarUrl && !avatarLoadFailed"
                class="user-menu__avatar"
                :src="avatarUrl"
                alt=""
                aria-hidden="true"
                @error="avatarLoadFailed = true"
              />
              <span v-else class="user-menu__avatar" aria-hidden="true" />
              <span class="user-menu__identity">
                <span v-if="displayName" class="user-menu__name">{{ displayName }}</span>
                <span v-if="userStore.userInfo.username" class="user-menu__account">
                  {{ userStore.userInfo.username }}
                </span>
              </span>
            </div>
            <el-dropdown-item divided @click="handleProfileClick">
              <AppIcon name="user" :size="16" class="user-menu__icon" />
              {{ t("navbar.profile") }}
            </el-dropdown-item>
            <el-dropdown-item @click="logout">
              <AppIcon name="logout" :size="16" class="user-menu__icon" />
              {{ t("navbar.logout") }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 系统设置 -->
    <button
      v-if="defaultSettings.showSettings"
      type="button"
      class="navbar-actions__item navbar-actions__button"
      :aria-label="t('navbar.settings')"
      @click="handleSettingsClick"
    >
      <AppIcon name="settings" :size="18" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { defaultSettings } from "@/settings";
import { DeviceEnum } from "@/enums/settings/device-enum";
import { useAppStore, useSettingsStore, useUserStore } from "@/store";

// 导入子组件
import MenuSearch from "@/components/MenuSearch/index.vue";
import Fullscreen from "@/components/Fullscreen/index.vue";
import ThemeToggle from "./ThemeToggle.vue";
import SizeSelect from "@/components/SizeSelect/index.vue";
import LangSelect from "@/components/LangSelect/index.vue";
import Notification from "@/components/Notification/index.vue";
import AppIcon from "@/components/AppIcon/index.vue";
import { resolveNavbarActionsTextClass } from "./navbarActionsHelpers";

const { t } = useI18n();
const appStore = useAppStore();
const settingStore = useSettingsStore();
const userStore = useUserStore();

const route = useRoute();
const router = useRouter();

// 是否为桌面设备
const isDesktop = computed(() => appStore.device === DeviceEnum.DESKTOP);

const avatarUrl = computed(() => userStore.userInfo.avatar);
const displayName = computed(() => userStore.userInfo.name || userStore.userInfo.username);
const avatarLoadFailed = ref(false);

// 更换头像后重新尝试加载
watch(avatarUrl, () => {
  avatarLoadFailed.value = false;
});

/**
 * 打开个人中心页面
 */
function handleProfileClick() {
  router.push({ name: "Profile" });
}

// 根据主题和侧边栏配色方案选择样式类
const navbarActionsClass = computed(() => {
  const { theme, sidebarColorScheme, layout } = settingStore;

  return resolveNavbarActionsTextClass({ theme, sidebarColorScheme, layout });
});

/**
 * 退出登录
 */
function logout() {
  ElMessageBox.confirm("确定注销并退出系统吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    lockScroll: false,
  })
    .then(async () => {
      try {
        await userStore.logout();
      } catch {
        ElMessage.warning("当前设备已退出，服务端令牌撤销未确认");
      } finally {
        await router.push({ path: "/login", query: { redirect: route.fullPath } });
      }
    })
    .catch((reason) => {
      if (reason !== "cancel" && reason !== "close") {
        ElMessage.error("退出操作未完成，请重试");
      }
    });
}

/**
 * 打开系统设置页面
 */
function handleSettingsClick() {
  settingStore.settingsVisible = true;
}
</script>

<style lang="scss" scoped>
.navbar-actions {
  display: flex;
  align-items: center;
  height: 100%;

  &__item {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 44px; /* 增加最小点击区域到44px，符合人机交互标准 */
    height: 100%;
    min-height: 44px;
    padding: 0 8px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;

    // 确保子元素居中
    > * {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    // 确保 Element Plus 组件可以正常工作
    :deep(.el-dropdown),
    :deep(.el-tooltip) {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
    }

    // 图标样式
    :deep(.app-icon) {
      font-size: 18px;
      line-height: 1;
      color: var(--el-text-color-regular);
      transition: color 0.3s;
    }

    &:hover {
      background: rgba(0, 0, 0, 0.04);

      :deep(.app-icon) {
        color: var(--el-color-primary);
      }
    }
  }

  &__search {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 8px 0 4px;
  }

  .user-profile {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 0 8px;

    &__avatar {
      flex-shrink: 0;
      width: 28px;
      height: 28px;
      border-radius: 50%;
    }

    &__name {
      margin-left: 8px;
      color: var(--el-text-color-regular);
      white-space: nowrap;
      transition: color 0.3s;
    }
  }
}

// 白色文字样式（用于深色背景：暗黑主题、顶部布局、混合布局）
.navbar-actions--white-text {
  .navbar-actions__item {
    :deep(.app-icon) {
      color: rgba(255, 255, 255, 0.85);
    }

    &:hover {
      background: rgba(255, 255, 255, 0.1);

      :deep(.app-icon) {
        color: #fff;
      }
    }
  }

  .user-profile__name {
    color: rgba(255, 255, 255, 0.85);
  }
}

// 深色文字样式（用于浅色背景：明亮主题下的左侧布局）
.navbar-actions--dark-text {
  .navbar-actions__item {
    :deep(.app-icon) {
      color: var(--el-text-color-regular) !important;
    }

    &:hover {
      background: rgba(0, 0, 0, 0.04);

      :deep(.app-icon) {
        color: var(--el-color-primary) !important;
      }
    }
  }

  .user-profile__name {
    color: var(--el-text-color-regular) !important;
  }
}

// 确保下拉菜单中的图标不受影响
:deep(.el-dropdown-menu) {
  .app-icon {
    color: var(--el-text-color-regular) !important;

    &:hover {
      color: var(--el-color-primary) !important;
    }
  }
}
</style>
