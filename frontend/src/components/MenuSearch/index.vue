<template>
  <button
    type="button"
    class="navbar-icon-button"
    :aria-label="t('navbar.search')"
    :title="t('menuSearch.shortcutHint', { key: shortcutKey })"
    @click="openSearchModal"
  >
    <AppIcon name="search" :size="18" />
  </button>

  <ProDialog
    v-model="isModalVisible"
    :title="t('navbar.search')"
    width="min(640px, calc(100vw - 24px))"
    :append-to-body="true"
    :show-close="false"
    :show-confirm-button="false"
    :cancel-text="t('menuSearch.close')"
    @close="closeSearchModal"
    @opened="searchInputRef?.focus()"
  >
    <template #header>
      <el-input
        ref="searchInputRef"
        v-model="searchKeyword"
        size="large"
        :placeholder="t('menuSearch.placeholder')"
        :aria-label="t('navbar.search')"
        clearable
        @keyup.enter="selectActiveResult"
        @input="updateSearchResults"
        @keydown.up.prevent="navigateResults('up')"
        @keydown.down.prevent="navigateResults('down')"
        @keydown.esc="closeSearchModal"
      >
        <template #prefix>
          <AppIcon name="search" :size="18" />
        </template>
      </el-input>
    </template>

    <div ref="resultsRef" class="search-result">
      <MenuSearchHistory
        v-if="searchKeyword === '' && searchHistory.length > 0"
        :items="searchHistory"
        :active-index="activeIndex"
        @clear="clearHistory"
        @remove="removeHistoryItem"
        @select="navigateToRoute"
      />

      <MenuSearchResultList
        v-else
        :active-index="activeIndex"
        :items="displayResults"
        @select="navigateToRoute"
      />

      <div v-if="searchKeyword === '' && searchHistory.length === 0" class="no-history">
        <p class="no-history__text">{{ t("menuSearch.noHistory") }}</p>
      </div>
      <div
        v-else-if="searchKeyword !== '' && displayResults.length === 0"
        class="no-history"
        role="status"
      >
        <p class="no-history__text">{{ t("menuSearch.noResults") }}</p>
      </div>
    </div>

    <template #footer>
      <MenuSearchFooter />
    </template>
  </ProDialog>
</template>

<script setup lang="ts">
import type { InputInstance } from "element-plus";
import ProDialog from "@/components/ProDialog/index.vue";
import AppIcon from "@/components/AppIcon/index.vue";
import router from "@/router";
import { usePermissionStore } from "@/store";
import { isExternal } from "@/utils";
import MenuSearchFooter from "./MenuSearchFooter.vue";
import MenuSearchHistory from "./MenuSearchHistory.vue";
import MenuSearchResultList from "./MenuSearchResultList.vue";
import { buildMenuSearchItems } from "./menu-search-routes";
import type { SearchDirection, SearchItem } from "./types";
import { useMenuSearchHistory } from "./useMenuSearchHistory";

const permissionStore = usePermissionStore();
const { t } = useI18n();
const isModalVisible = ref(false);
const searchKeyword = ref("");
const searchInputRef = ref<InputInstance>();
const resultsRef = ref<HTMLElement>();
const menuItems = computed(() => buildMenuSearchItems(permissionStore.routes));
const shortcutKey = /Mac|iPhone|iPad/.test(navigator.platform) ? "Cmd" : "Ctrl";
const activeIndex = ref(-1);

const { addToHistory, clearHistory, loadSearchHistory, removeHistoryItem, searchHistory } =
  useMenuSearchHistory();

// 注册全局快捷键
function handleKeyDown(e: KeyboardEvent) {
  // 判断是否为Ctrl+K组合键
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault(); // 阻止默认行为
    openSearchModal();
  }
}

// 添加键盘事件监听
onMounted(() => {
  loadSearchHistory();
  document.addEventListener("keydown", handleKeyDown);
});

// 移除键盘事件监听
onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeyDown);
});

// 打开搜索模态框
function openSearchModal() {
  searchKeyword.value = "";
  activeIndex.value = -1;
  isModalVisible.value = true;
}

// 关闭搜索模态框
function closeSearchModal() {
  isModalVisible.value = false;
}

// 更新搜索结果
function updateSearchResults() {
  activeIndex.value = displayResults.value.length > 0 ? 0 : -1;
}

// 显示搜索结果
const displayResults = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();
  return keyword
    ? menuItems.value.filter((item) => item.title.toLowerCase().includes(keyword))
    : searchHistory.value;
});

watch(activeIndex, async () => {
  await nextTick();
  resultsRef.value?.querySelector('[data-active="true"]')?.scrollIntoView({ block: "nearest" });
});

// 执行搜索
function selectActiveResult() {
  const item = displayResults.value[Math.max(0, activeIndex.value)];
  if (item) navigateToRoute(item);
}

// 导航搜索结果
function navigateResults(direction: SearchDirection) {
  if (displayResults.value.length === 0) return;

  if (direction === "up") {
    activeIndex.value =
      activeIndex.value <= 0 ? displayResults.value.length - 1 : activeIndex.value - 1;
  } else if (direction === "down") {
    activeIndex.value =
      activeIndex.value >= displayResults.value.length - 1 ? 0 : activeIndex.value + 1;
  }
}

// 跳转到
function navigateToRoute(item: SearchItem) {
  closeSearchModal();
  // 添加到历史记录
  addToHistory(item);

  if (isExternal(item.path)) {
    window.open(item.path, "_blank");
  } else {
    router.push({ path: item.path, query: item.params });
  }
}
</script>

<style scoped lang="scss">
.search-result {
  max-height: 400px;
  overflow-y: auto;
}

/* 没有搜索历史时的样式 */
.no-history {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;

  &__text {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

// 适配Element Plus对话框
:deep(.el-dialog__footer) {
  box-sizing: border-box;
  padding-top: 10px;
  text-align: right;
}
</style>
