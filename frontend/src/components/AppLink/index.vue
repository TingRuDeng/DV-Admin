<template>
  <component :is="linkType" v-bind="mergedProps">
    <slot />
  </component>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import type { LocationQueryRaw } from "vue-router";

defineOptions({
  name: "AppLink",
  inheritAttrs: false,
});

import { isExternal } from "@/utils/index";

interface AppLinkTo {
  path: string;
  query?: LocationQueryRaw;
}

type ExternalLinkProps = {
  href: string;
  target: "_blank";
  rel: "noopener noreferrer";
};

type InternalLinkProps = {
  to: AppLinkTo;
};

const attrs = useAttrs();

const props = defineProps({
  to: {
    type: Object as PropType<AppLinkTo>,
    required: true,
  },
});

const isExternalLink = computed(() => {
  return isExternal(props.to.path);
});

const linkType = computed(() => (isExternalLink.value ? "a" : "router-link"));

function buildLinkProps(to: AppLinkTo): ExternalLinkProps | InternalLinkProps {
  if (isExternalLink.value) {
    return {
      href: to.path,
      target: "_blank",
      rel: "noopener noreferrer",
    };
  }
  return { to };
}

const mergedProps = computed(() => ({
  ...attrs,
  ...buildLinkProps(props.to),
}));
</script>
