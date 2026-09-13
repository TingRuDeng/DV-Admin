<template>
  <div
    ref="iconSelectRef"
    :style="{ width: props.width, maxWidth: '100%' }"
    @keydown.esc.stop.prevent="closePopover"
  >
    <el-popover
      :visible="popoverVisible"
      width="min(500px, calc(100vw - 32px))"
      placement="bottom-end"
      @after-enter="searchRef?.focus()"
    >
      <template #reference>
        <div class="icon-select-preview">
          <button
            ref="triggerRef"
            type="button"
            class="icon-select-trigger"
            :aria-expanded="popoverVisible"
            :aria-label="t('iconSelect.select')"
            @click="togglePopover"
          >
            <slot>
              <AppIcon :name="previewIcon" :size="18" />
              <span class="icon-select-preview__value">
                {{ selectedIcon || t("iconSelect.placeholder") }}
              </span>
            </slot>
            <AppIcon
              :name="popoverVisible ? 'arrow-up' : 'arrow-down'"
              :size="16"
              class="icon-select-preview__chevron"
            />
          </button>
          <button
            v-if="selectedIcon"
            type="button"
            class="icon-select-preview__clear"
            :aria-label="t('iconSelect.clear')"
            :title="t('iconSelect.clear')"
            @click="clearSelectedIcon"
          >
            <AppIcon name="x" :size="15" />
          </button>
        </div>
      </template>

      <div
        ref="popoverContentRef"
        class="icon-select-popover"
        @keydown.esc.stop.prevent="closePopover"
      >
        <el-input
          ref="searchRef"
          v-model="filterText"
          :placeholder="t('iconSelect.search')"
          :aria-label="t('iconSelect.search')"
          clearable
        />
        <ul class="icon-grid" :aria-label="t('iconSelect.listLabel')">
          <li v-for="icon in filteredIcons" :key="icon" class="icon-grid-item">
            <button type="button" :aria-label="icon" @click="selectIcon(icon)">
              <AppIcon :name="icon" :size="20" />
              <span>{{ icon }}</span>
            </button>
          </li>
        </ul>
        <p v-if="filteredIcons.length === 0" class="icon-select-empty" role="status">
          {{ t("iconSelect.noResults") }}
        </p>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import type { InputInstance } from "element-plus";
import { APP_ICON_NAMES, normalizeAppIconName } from "@/components/AppIcon/icon-map";

const { t } = useI18n();

const props = defineProps({
  width: {
    type: String,
    default: "100%",
  },
});

const selectedIcon = defineModel<string>({ default: "" });
const iconSelectRef = ref<HTMLElement>();
const popoverContentRef = ref<HTMLElement>();
const popoverVisible = ref(false);
const filterText = ref("");
const triggerRef = ref<HTMLButtonElement>();
const searchRef = ref<InputInstance>();

const previewIcon = computed(() => normalizeAppIconName(selectedIcon.value || "menu"));
const filteredIcons = computed(() => {
  const keyword = filterText.value.trim().toLowerCase();
  return keyword ? APP_ICON_NAMES.filter((icon) => icon.includes(keyword)) : APP_ICON_NAMES;
});

function selectIcon(icon: string) {
  selectedIcon.value = icon;
  closePopover();
}

function closePopover() {
  popoverVisible.value = false;
  triggerRef.value?.focus();
}

function togglePopover() {
  popoverVisible.value = !popoverVisible.value;
}

function clearSelectedIcon() {
  selectedIcon.value = "";
  triggerRef.value?.focus();
}

onClickOutside(iconSelectRef, () => (popoverVisible.value = false), {
  ignore: [popoverContentRef],
});
</script>

<style scoped lang="scss">
.icon-select-trigger {
  display: flex;
  flex: 1;
  gap: 10px;
  align-items: center;
  min-width: 0;
  min-height: 34px;
  padding: 5px 10px;
  font: inherit;
  color: inherit;
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 0;
}

.icon-select-preview {
  display: flex;
  align-items: center;
  min-height: 32px;
  color: var(--el-text-color-primary);
  background: var(--el-fill-color-blank);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease;

  &:hover,
  &:focus-within {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--el-color-primary) 14%, transparent);
  }

  &__value {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
  }

  &__clear {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 34px;
    min-height: 34px;
    padding: 6px;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    background: transparent;
    border: 0;

    &:hover {
      color: var(--el-color-danger);
    }
  }

  &__chevron {
    color: var(--el-text-color-secondary);
  }
}

.icon-select-popover {
  display: grid;
  gap: 12px;
}

.icon-select-empty {
  padding: 24px 0;
  margin: 0;
  color: var(--el-text-color-secondary);
  text-align: center;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(84px, 1fr));
  max-height: 300px;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  list-style: none;
}

.icon-grid-item button {
  display: grid;
  gap: 6px;
  place-items: center;
  width: 100%;
  min-height: 64px;
  padding: 8px;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;

  &:hover,
  &:focus-visible {
    color: var(--el-color-primary);
    outline: none;
    background: var(--el-fill-color-light);
    border-color: var(--el-color-primary-light-7);
  }

  span {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 11px;
    white-space: nowrap;
  }
}
</style>
