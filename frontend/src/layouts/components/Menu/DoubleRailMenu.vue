<!-- 双列布局左侧图标栏：一级菜单图标在上、名称在下 -->
<template>
  <ul class="double-rail">
    <li v-for="menu in topMenus" :key="menu.path">
      <button
        type="button"
        class="double-rail__item"
        :class="{ 'is-active': menu.path === activeTopMenuPath }"
        :aria-current="menu.path === activeTopMenuPath ? 'true' : undefined"
        @click="handleSelect(menu.path)"
      >
        <AppIcon :name="iconName(menu.meta?.icon)" :size="20" class="double-rail__icon" />
        <span class="double-rail__label">{{ translateRouteTitle(menu.meta?.title) }}</span>
      </button>
    </li>
  </ul>
</template>

<script lang="ts" setup>
import AppIcon from "@/components/AppIcon/index.vue";
import { normalizeMenuIconName } from "@/components/AppIcon/icon-map";
import { isExternal } from "@/utils";
import { translateRouteTitle } from "@/utils/i18n";
import { useTopMenuNavigation } from "./useTopMenuNavigation";

defineOptions({ name: "DoubleRailMenu" });

const { activeTopMenuPath, selectTopMenu, topMenus } = useTopMenuNavigation();

function iconName(icon?: unknown) {
  return normalizeMenuIconName(typeof icon === "string" ? icon : undefined);
}

function handleSelect(path: string) {
  if (isExternal(path)) {
    window.open(path, "_blank", "noopener");
    return;
  }
  selectTopMenu(path);
}
</script>

<style lang="scss" scoped>
.double-rail {
  display: grid;
  gap: 4px;
  padding: 8px 6px;
  margin: 0;
  list-style: none;
}

.double-rail__item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 58px;
  padding: 8px 4px;
  color: var(--ff-shell-text-muted);
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 14px;
  transition:
    color var(--ff-duration-fast) ease,
    background-color var(--ff-duration-fast) ease;

  &:hover {
    color: var(--ff-shell-text);
    background: var(--ff-shell-hover);
  }

  &:focus-visible {
    outline: 2px solid var(--el-color-primary-light-5);
    outline-offset: 1px;
  }

  &.is-active {
    color: var(--ff-accent);
    background:
      linear-gradient(
        100deg,
        color-mix(in srgb, var(--ff-iri-a) 16%, transparent),
        color-mix(in srgb, var(--ff-iri-c) 8%, transparent)
      ),
      var(--ff-shell-active);
  }
}

.double-rail__icon {
  flex: none;
}

.double-rail__label {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
}

.is-active .double-rail__label {
  font-weight: 600;
}
</style>
