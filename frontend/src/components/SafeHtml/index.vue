<template>
  <div class="safe-html" v-html="safeHtml" />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { sanitizeHtml } from "@/utils/safe-html";

const props = defineProps<{
  content?: string | null;
}>();

const safeHtml = computed(() => sanitizeHtml(props.content));
</script>
