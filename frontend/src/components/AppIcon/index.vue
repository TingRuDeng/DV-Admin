<template>
  <component
    :is="icon"
    v-bind="$attrs"
    :size="size"
    :stroke-width="strokeWidth"
    :aria-label="label || undefined"
    :aria-hidden="label ? undefined : true"
    class="app-icon"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { resolveAppIcon } from "./icon-map";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    name: string;
    size?: number | string;
    strokeWidth?: number;
    label?: string;
  }>(),
  {
    size: 18,
    strokeWidth: 1.8,
    label: undefined,
  }
);

const icon = computed(() => resolveAppIcon(props.name));
</script>
