<template>
  <section class="dashboard-hero ff-page-shell__hero--dashboard" aria-labelledby="dashboard-title">
    <p class="dashboard-hero__clock" role="timer">
      <template v-for="(part, index) in clockParts" :key="index">
        <i v-if="index" class="dashboard-hero__sep">:</i>
        <span class="dashboard-hero__digits" :style="{ '--i': index }" v-text="part" />
      </template>
    </p>

    <div class="dashboard-hero__identity">
      <div class="dashboard-hero__avatar">
        <img v-if="avatar" :src="avatar" :alt="`${name} 的头像`" />
      </div>
      <h1 id="dashboard-title" class="dashboard-hero__title">
        <span class="dashboard-hero__greeting">你好，</span>
        <span class="dashboard-hero__name">{{ name }}</span>
      </h1>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  name: string;
  avatar?: string;
  currentTime: string;
}>();

// 按冒号拆段，逐段入场；最后一段（分钟）用虹彩渐变字
const clockParts = computed(() => props.currentTime.split(":"));
</script>
