<template>
  <div class="menu-search">
    <!-- 外层在文档流里固定占位，胶囊绝对定位，聚焦时向左展开盖住左侧内容，布局不重排 -->
    <label ref="fieldRef" class="menu-search__field">
      <AppIcon name="search" :size="16" class="menu-search__icon" />
      <input
        ref="inputRef"
        v-model="keyword"
        type="text"
        class="menu-search__input"
        role="combobox"
        autocomplete="off"
        spellcheck="false"
        :placeholder="t('navbar.search')"
        :aria-label="t('navbar.search')"
        aria-autocomplete="list"
        :aria-expanded="isListboxVisible ? 'true' : 'false'"
        :aria-controls="listboxId"
        :aria-activedescendant="activeOptionId"
        @focus="openPanel"
        @blur="closePanel"
        @click="openPanel"
        @input="openPanel"
        @keydown="handleKeydown"
      />
      <kbd class="menu-search__kbd" aria-hidden="true">{{ shortcutLabel }}</kbd>
    </label>

    <Teleport to="body">
      <!--
        按下时阻止默认行为，点击选项或按钮不会先让输入框失焦把面板收掉。
        必须用 pointerdown：main.ts 引入的 default-passive-events 把 mousedown 监听默认设成 passive，preventDefault 无效
      -->
      <div
        v-show="isPanelVisible"
        class="menu-search__panel"
        :style="panelStyle"
        @pointerdown.prevent
      >
        <ul
          v-show="isListboxVisible"
          :id="listboxId"
          role="listbox"
          class="menu-search__listbox"
          :aria-label="isHistoryMode ? t('navbar.searchHistory') : t('navbar.searchResults')"
        >
          <!-- 收起时不渲染选项，页面里不留一份隐藏的菜单标题 -->
          <template v-if="isPanelOpen">
            <MenuSearchHistory
              v-if="isHistoryMode"
              :active-index="activeIndex"
              :id-prefix="optionIdPrefix"
              :items="searchHistory"
              @remove="removeHistoryAt"
              @select="selectItem"
            />
            <MenuSearchResultList
              v-else
              :active-index="activeIndex"
              :id-prefix="optionIdPrefix"
              :items="searchResults"
              @select="selectItem"
            />
          </template>
        </ul>

        <p v-if="isNoMatch" class="menu-search__empty" role="status">
          {{ t("navbar.searchNoMatch") }}
        </p>

        <div v-if="isHistoryMode && isListboxVisible" class="menu-search__footer">
          <button type="button" class="menu-search__clear" @click="clearHistory">
            {{ t("navbar.clearSearchHistory") }}
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, useId, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useElementBounding, useEventListener } from "@vueuse/core";
import AppIcon from "@/components/AppIcon/index.vue";
import { usePermissionStore } from "@/store";
import { isExternal } from "@/utils";
import MenuSearchHistory from "./MenuSearchHistory.vue";
import MenuSearchResultList from "./MenuSearchResultList.vue";
import { buildMenuSearchItems } from "./menu-search-routes";
import type { SearchItem } from "./types";
import { useMenuSearchHistory } from "./useMenuSearchHistory";
import { useMenuSearchShortcut } from "./useMenuSearchShortcut";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const permissionStore = usePermissionStore();

const baseId = `menu-search-${useId()}`;
const listboxId = `${baseId}-listbox`;
const optionIdPrefix = `${baseId}-option`;

const fieldRef = ref<HTMLElement>();
const inputRef = ref<HTMLInputElement>();
const keyword = ref("");
const isPanelOpen = ref(false);
const activeIndex = ref(-1);

const { addToHistory, clearHistory, loadSearchHistory, removeHistoryItem, searchHistory } =
  useMenuSearchHistory();
const { shortcutLabel } = useMenuSearchShortcut(focusInput);

// 菜单跟随权限路由重新生成，路由晚于组件挂载注入时也能搜到
const menuItems = computed(() => buildMenuSearchItems(permissionStore.routes));
const normalizedKeyword = computed(() => keyword.value.trim().toLowerCase());
const isHistoryMode = computed(() => normalizedKeyword.value === "");
const searchResults = computed(() =>
  isHistoryMode.value
    ? []
    : menuItems.value.filter((item) => item.title.toLowerCase().includes(normalizedKeyword.value))
);
const options = computed(() => (isHistoryMode.value ? searchHistory.value : searchResults.value));

// listbox 只在有选项时展开；有关键字却没有匹配时，面板只显示空状态
const isListboxVisible = computed(() => isPanelOpen.value && options.value.length > 0);
const isNoMatch = computed(
  () => isPanelOpen.value && !isHistoryMode.value && searchResults.value.length === 0
);
const isPanelVisible = computed(() => isListboxVisible.value || isNoMatch.value);
const activeOptionId = computed(() =>
  isListboxVisible.value && activeIndex.value >= 0 && activeIndex.value < options.value.length
    ? `${optionIdPrefix}-${activeIndex.value}`
    : undefined
);

// 面板传送到 body，右边缘对齐胶囊右边缘（胶囊只向左展开，右边缘不动）
const {
  bottom: fieldBottom,
  right: fieldRight,
  update: updateFieldBounding,
} = useElementBounding(fieldRef);
const panelStyle = computed(() => ({
  top: `${fieldBottom.value + 8}px`,
  left: `${fieldRight.value}px`,
}));

// left 布局的主内容区是内部滚动容器，window 上收不到 scroll，用捕获阶段兜底
useEventListener(
  document,
  "scroll",
  () => {
    if (isPanelVisible.value) updateFieldBounding();
  },
  { capture: true, passive: true }
);

onMounted(loadSearchHistory);

watch(normalizedKeyword, () => {
  activeIndex.value = -1;
});
watch(() => route.fullPath, closePanel);

function openPanel() {
  updateFieldBounding();
  isPanelOpen.value = true;
}

function closePanel() {
  isPanelOpen.value = false;
  activeIndex.value = -1;
}

function focusInput() {
  inputRef.value?.focus();
  inputRef.value?.select();
  openPanel();
}

// 上下键循环高亮，并把高亮项滚到可见区域
function moveActive(step: 1 | -1) {
  const count = options.value.length;
  if (count === 0) return;

  if (activeIndex.value < 0) {
    activeIndex.value = step > 0 ? 0 : count - 1;
  } else {
    activeIndex.value = (activeIndex.value + step + count) % count;
  }

  const optionId = `${optionIdPrefix}-${activeIndex.value}`;
  nextTick(() => document.getElementById(optionId)?.scrollIntoView({ block: "nearest" }));
}

// 删除后高亮留在原位置，指向下一项；删的是最后一项时退回上一项
function removeHistoryAt(index: number) {
  removeHistoryItem(index);
  if (activeIndex.value > index || activeIndex.value >= searchHistory.value.length) {
    activeIndex.value -= 1;
  }
}

function handleKeydown(event: KeyboardEvent) {
  // 输入法组字时的回车、方向键属于输入法
  if (event.isComposing) return;

  switch (event.key) {
    case "ArrowDown":
    case "ArrowUp":
      event.preventDefault();
      openPanel();
      moveActive(event.key === "ArrowDown" ? 1 : -1);
      break;
    case "Enter": {
      // 有高亮选高亮项，没有高亮时回车直接选第一个匹配
      const item = isListboxVisible.value
        ? (options.value[activeIndex.value] ?? searchResults.value[0])
        : searchResults.value[0];
      if (!item) return;
      event.preventDefault();
      selectItem(item);
      break;
    }
    case "Escape":
      if (!isPanelVisible.value) return;
      event.preventDefault();
      closePanel();
      break;
    case "Tab":
      closePanel();
      break;
    case "Delete":
      if (!isHistoryMode.value || !activeOptionId.value) return;
      event.preventDefault();
      removeHistoryAt(activeIndex.value);
      break;
  }
}

function selectItem(item: SearchItem) {
  addToHistory(item);
  keyword.value = "";
  closePanel();
  inputRef.value?.blur();

  if (isExternal(item.path)) {
    window.open(item.path, "_blank", "noopener");
  } else {
    router.push({ path: item.path, query: item.params });
  }
}
</script>
