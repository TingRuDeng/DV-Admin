<template>
  <section class="ff-page-shell" :class="{ 'ff-page-shell--fill': fill }">
    <slot />
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    fill?: boolean;
  }>(),
  {
    fill: true,
  }
);
</script>
