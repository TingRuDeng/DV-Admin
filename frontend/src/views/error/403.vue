<template>
  <div class="error-page" role="main">
    <div class="error-page__visual" aria-hidden="true">
      <img src="@/assets/images/401.svg" alt="" class="error-page__image" />
    </div>
    <div class="error-page__content">
      <p class="error-page__code">403</p>
      <h1 class="error-page__title">{{ t("error.forbiddenTitle") }}</h1>
      <p class="error-page__desc">{{ t("error.forbiddenDesc") }}</p>
      <div class="error-page__actions">
        <el-button type="primary" round class="error-page__btn" @click="router.push('/dashboard')">
          <AppIcon name="homepage" :size="16" />
          {{ t("error.backHome") }}
        </el-button>
        <el-button round class="error-page__btn" @click="router.back()">
          <AppIcon name="arrow-left" :size="16" />
          {{ t("error.goBack") }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";

defineOptions({ name: "Page403" });
const router = useRouter();
const { t } = useI18n();
</script>

<style lang="scss" scoped>
@use "@/styles/variables.scss" as vars;
@import "./error-page";
</style>
