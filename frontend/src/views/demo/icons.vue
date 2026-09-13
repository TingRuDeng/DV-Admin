<template>
  <PageShell class="ff-demo-page">
    <div class="icons-container">
      <div class="icons-container__header">
        <span class="icons-container__eyebrow">{{ t("iconsDemo.eyebrow") }}</span>
        <h1>{{ t("iconsDemo.title") }}</h1>
      </div>
      <div class="grid">
        <div v-for="name of APP_ICON_NAMES" :key="name">
          <CopyButton :text="name">
            <el-tooltip effect="dark" :content="t('iconsDemo.copy', { name })" placement="top">
              <div class="icon-item">
                <AppIcon :name="name" :size="24" />
                <span>{{ name }}</span>
              </div>
            </el-tooltip>
          </CopyButton>
        </div>
      </div>
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import { APP_ICON_NAMES } from "@/components/AppIcon/icon-map";
import PageShell from "@/components/PageShell/index.vue";

const { t } = useI18n();

defineOptions({
  name: "Icons",
  inheritAttrs: false,
});
</script>

<style lang="scss" scoped>
.icons-container {
  max-width: 1440px;
  padding: 32px;
  margin: 0 auto;

  &__header {
    margin-bottom: 28px;

    h1 {
      margin: 6px 0 4px;
      font-size: clamp(28px, 4vw, 52px);
      font-weight: 700;
      letter-spacing: -0.04em;
    }

    p {
      margin: 0;
      color: var(--el-text-color-secondary);
    }
  }

  &__eyebrow {
    font-size: 11px;
    font-weight: 700;
    color: var(--ff-accent);
    letter-spacing: 0.2em;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(118px, 1fr));
    gap: 10px;
  }

  .icon-item {
    display: grid;
    gap: 10px;
    place-items: center;
    width: 100%;
    min-height: 92px;
    padding: 16px 10px;
    color: var(--el-text-color-regular);
    cursor: pointer;
    background: var(--el-fill-color-blank);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 12px;
    transition:
      border-color 160ms ease,
      color 160ms ease,
      transform 160ms ease;

    &:hover,
    &:focus-visible {
      color: var(--ff-accent);
      outline: none;
      border-color: var(--ff-accent);
      transform: translateY(-2px);
    }

    span {
      width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 11px;
      text-align: center;
      white-space: nowrap;
    }
  }
}
</style>
