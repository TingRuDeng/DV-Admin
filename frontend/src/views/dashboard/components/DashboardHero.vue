<template>
  <section class="dashboard-hero ff-page-shell__hero--dashboard" aria-labelledby="dashboard-title">
    <div class="dashboard-hero__grid" aria-hidden="true"></div>
    <div class="dashboard-hero__beam dashboard-hero__beam--coral" aria-hidden="true"></div>
    <div class="dashboard-hero__beam dashboard-hero__beam--blue" aria-hidden="true"></div>

    <div class="dashboard-hero__content">
      <div class="dashboard-hero__meta">
        <span class="dashboard-hero__signal"></span>
        <span>{{ t("dashboard.workspace") }} / {{ currentTime }}</span>
      </div>
      <h1 id="dashboard-title" class="dashboard-hero__title">
        {{ t("dashboard.greeting") }}
        <span>{{ name }}</span>
      </h1>
    </div>

    <div class="dashboard-hero__identity">
      <div class="dashboard-hero__avatar">
        <img
          v-if="avatar && !avatarFailed"
          :src="avatar"
          :alt="t('dashboard.avatarAlt', { name })"
          @error="avatarFailed = true"
        />
        <AppIcon v-else name="user-round" :size="28" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import AppIcon from "@/components/AppIcon/index.vue";
import { ref, watch } from "vue";

const { t } = useI18n();

const props = defineProps<{
  name: string;
  avatar?: string;
  currentTime: string;
}>();
const avatarFailed = ref(false);
watch(
  () => props.avatar,
  () => {
    avatarFailed.value = false;
  }
);
</script>
