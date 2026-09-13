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
        <div class="ff-error-page__code" aria-hidden="true">404</div>
        <h1 id="error-title" class="ff-error-page__title">{{ t("error.notFound") }}</h1>
        <el-button class="ff-error-page__action" @click="back">{{ t("error.home") }}</el-button>
      </section>
      <div class="ff-error-page__art">
        <img src="@/assets/images/404.svg" alt="" />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
defineOptions({ name: "Page404" });
const router = useRouter();
const { t } = useI18n();
const back = () => router.push("/");
</script>
