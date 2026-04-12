<template>
  <section class="ff-data-panel">
    <header class="ff-data-panel__header">
      <div class="ff-data-panel__title">
        <slot name="title">
          <span>{{ title }}</span>
        </slot>
      </div>
      <div v-if="$slots.actions" class="ff-data-panel__actions">
        <slot name="actions" />
      </div>
    </header>

    <div class="ff-data-panel__body">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="ff-data-panel__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>
