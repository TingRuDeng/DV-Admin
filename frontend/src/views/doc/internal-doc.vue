<template>
  <PageShell class="ff-doc-page">
    <section class="ff-doc-page__empty">
      <AppIcon name="book-open" :size="48" />
      <h1>{{ t("documentation.empty") }}</h1>
      <RouterLink to="/dashboard" class="ff-doc-page__back">{{ t("error.home") }}</RouterLink>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import AppIcon from "@/components/AppIcon/index.vue";
const { t } = useI18n();
</script>
