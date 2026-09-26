import { useDraggable } from "vue-draggable-plus";
import type { SortableEvent } from "sortablejs";
import { useAppStore, useTagsViewStore } from "@/store";
import { DeviceEnum } from "@/enums/settings/device-enum";

/**
 * 页签拖拽排序：只在桌面端启用，固定页签不能拖动，也不能被挤到后面
 */
export function useTagsDrag(container: Ref<HTMLElement | undefined>) {
  const appStore = useAppStore();
  const tagsViewStore = useTagsViewStore();
  const isDesktop = computed(() => appStore.device === DeviceEnum.DESKTOP);

  const draggable = useDraggable(container, {
    animation: 180,
    draggable: ".tags-view-item",
    filter: ".is-affix",
    preventOnFilter: false,
    ghostClass: "is-drag-ghost",
    chosenClass: "is-drag-chosen",
    immediate: false,
    // 不直接改列表，交给 store 按固定页签规则落位；落位失败时列表保持原样
    customUpdate: (event: SortableEvent) => {
      if (event.oldIndex === undefined || event.newIndex === undefined) return;
      tagsViewStore.moveVisitedView(event.oldIndex, event.newIndex);
    },
    onMove: (event) => !event.related.classList.contains("is-affix"),
  });

  watch(
    [isDesktop, container],
    ([desktop, element]) => {
      draggable.destroy();
      if (desktop && element) {
        draggable.start(element);
      }
    },
    { flush: "post" }
  );

  onBeforeUnmount(() => draggable.destroy());
}
