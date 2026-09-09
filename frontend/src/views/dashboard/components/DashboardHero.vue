<template>
  <section class="dashboard-hero ff-page-shell__hero--dashboard" aria-labelledby="dashboard-title">
    <div class="dashboard-hero__grid" aria-hidden="true"></div>
    <div class="dashboard-hero__beam dashboard-hero__beam--coral" aria-hidden="true"></div>
    <div class="dashboard-hero__beam dashboard-hero__beam--blue" aria-hidden="true"></div>

    <div class="dashboard-hero__content">
      <div class="dashboard-hero__meta">
        <span class="dashboard-hero__signal"></span>
        <span>Workspace / {{ currentTime }}</span>
      </div>
      <h1 id="dashboard-title" class="dashboard-hero__title">
        你好，
        <span>{{ name }}</span>
      </h1>
    </div>

    <div class="dashboard-hero__identity">
      <div class="dashboard-hero__avatar">
        <img v-if="avatar" :src="avatar" :alt="`${name} 的头像`" />
        <AppIcon v-else name="user-round" :size="28" />
      </div>
      <AppIcon name="arrow-right" :size="18" class="dashboard-hero__arrow" />
    </div>

    <div class="dashboard-hero__index" aria-hidden="true">01</div>
  </section>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";

defineProps<{
  name: string;
  avatar?: string;
  currentTime: string;
}>();
</script>
