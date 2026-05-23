<template>
  <div @click="openSearchModal">
    <div class="i-svg:search" />
    <ProDialog
      v-model="isModalVisible"
      width="30%"
      :append-to-body="true"
      :show-close="false"
      :show-confirm-button="false"
      cancel-text="关闭"
      @close="closeSearchModal"
    >
      <template #header>
        <el-input
          ref="searchInputRef"
          v-model="searchKeyword"
          size="large"
          placeholder="输入菜单名称关键字搜索"
          clearable
          @keyup.enter="selectActiveResult"
          @input="updateSearchResults"
          @keydown.up.prevent="navigateResults('up')"
          @keydown.down.prevent="navigateResults('down')"
          @keydown.esc="closeSearchModal"
        >
          <template #prepend>
            <el-button icon="Search" />
          </template>
        </el-input>
      </template>

      <div class="search-result">
        <MenuSearchHistory
          v-if="searchKeyword === '' && searchHistory.length > 0"
          :items="searchHistory"
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

        <!-- 无搜索历史显示 -->
        <div v-if="searchKeyword === '' && searchHistory.length === 0" class="no-history">
          <p class="no-history__text">没有搜索历史</p>
        </div>
      </div>

      <template #footer>
        <MenuSearchFooter />
      </template>
    </ProDialog>
  </div>
</template>

<script setup lang="ts">
import ProDialog from "@/components/ProDialog/index.vue";
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
const isModalVisible = ref(false);
const searchKeyword = ref("");
const searchInputRef = ref();
const menuItems = ref<SearchItem[]>([]);
const searchResults = ref<SearchItem[]>([]);
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
  menuItems.value = buildMenuSearchItems(permissionStore.routes);
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
  setTimeout(() => {
    searchInputRef.value.focus();
  }, 100);
}

// 关闭搜索模态框
function closeSearchModal() {
  isModalVisible.value = false;
}

// 更新搜索结果
function updateSearchResults() {
  activeIndex.value = -1;
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    searchResults.value = menuItems.value.filter((item) =>
      item.title.toLowerCase().includes(keyword)
    );
  } else {
    searchResults.value = [];
  }
}

// 显示搜索结果
const displayResults = computed(() => searchResults.value);

// 执行搜索
function selectActiveResult() {
  if (displayResults.value.length > 0 && activeIndex.value >= 0) {
    navigateToRoute(displayResults.value[activeIndex.value]);
  }
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
