import { useElementHover } from "@vueuse/core";
import { sanitizeHtml } from "@/utils/safe-html";
import type { TextScrollProps } from "./types";

export function useTextScroll(props: Required<TextScrollProps>) {
  const containerRef = ref<HTMLElement | null>(null);
  const scrollContent = ref<HTMLElement | null>(null);
  const isHovered = useElementHover(containerRef);
  const animationDuration = ref(0);
  const currentText = ref("");
  const isTypewriterComplete = ref(false);
  let typewriterTimer: ReturnType<typeof setTimeout> | null = null;

  const shouldScroll = computed(() => {
    if (props.typewriter) {
      return !isHovered.value && isTypewriterComplete.value;
    }
    return !isHovered.value;
  });

  const sanitizedContent = computed(() =>
    sanitizeHtml(props.typewriter ? currentText.value : props.text)
  );

  const scrollStyle = computed(() => ({
    "--animation-duration": `${animationDuration.value}s`,
    "--animation-play-state": shouldScroll.value ? "running" : "paused",
    "--animation-direction": props.direction === "left" ? "normal" : "reverse",
  }));

  function calculateDuration() {
    if (!scrollContent.value) return;
    const contentWidth = scrollContent.value.scrollWidth / 2;
    animationDuration.value = contentWidth / props.speed;
  }

  function clearTypewriterTimer() {
    if (!typewriterTimer) return;
    clearTimeout(typewriterTimer);
    typewriterTimer = null;
  }

  function startTypewriter() {
    let index = 0;
    currentText.value = "";
    isTypewriterComplete.value = false;

    const type = () => {
      if (index < props.text.length) {
        currentText.value += props.text[index];
        index += 1;
        typewriterTimer = setTimeout(type, props.typewriterSpeed);
        return;
      }

      isTypewriterComplete.value = true;
    };

    type();
  }

  onMounted(() => {
    calculateDuration();
    window.addEventListener("resize", calculateDuration);

    if (props.typewriter) {
      startTypewriter();
    }
  });

  onUnmounted(() => {
    window.removeEventListener("resize", calculateDuration);
    clearTypewriterTimer();
  });

  watch(
    () => props.text,
    () => {
      if (!props.typewriter) return;
      clearTypewriterTimer();
      startTypewriter();
    }
  );

  return {
    containerRef,
    sanitizedContent,
    scrollContent,
    scrollStyle,
    shouldScroll,
  };
}
