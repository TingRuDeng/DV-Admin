<template>
  <main class="ff-error-page">
    <el-button
      class="ff-error-page__back"
      :icon="resolveAppIcon('arrow-left')"
      @click="router.back()"
    >
      {{ t("error.back") }}
    </el-button>
    <div class="ff-error-page__grid">
      <section class="ff-error-page__content" aria-labelledby="error-title">
        <div class="ff-error-page__code" aria-hidden="true">403</div>
        <h1 id="error-title" class="ff-error-page__title">{{ t("error.accessDenied") }}</h1>
        <el-button class="ff-error-page__action" @click="router.push('/dashboard')">
          {{ t("error.home") }}
        </el-button>
      </section>
      <div class="ff-error-page__art">
        <img src="@/assets/images/401.svg" alt="" />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
defineOptions({ name: "Page403" });
const router = useRouter();
const { t } = useI18n();
</script>
