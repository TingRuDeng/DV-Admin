interface ContextMenu {
  visible: boolean;
  x: number;
  y: number;
}

export function useTagsContextMenu(visitedViews: Ref<TagView[]>) {
  const selectedTag = ref<TagView | null>(null);
  const contextMenu = reactive<ContextMenu>({
    visible: false,
    x: 0,
    y: 0,
  });

  const isFirstView = computed(() => {
    if (!selectedTag.value) return false;
    return (
      selectedTag.value.path === "/dashboard" ||
      selectedTag.value.fullPath === visitedViews.value[1]?.fullPath
    );
  });

  const isLastView = computed(() => {
    if (!selectedTag.value) return false;
    return (
      selectedTag.value.fullPath === visitedViews.value[visitedViews.value.length - 1]?.fullPath
    );
  });

  function openContextMenu(tag: TagView, event: MouseEvent) {
    contextMenu.x = event.clientX;
    contextMenu.y = event.clientY;
    contextMenu.visible = true;
    selectedTag.value = tag;
  }

  function closeContextMenu() {
    contextMenu.visible = false;
  }

  function useContextMenuManager() {
    const handleOutsideClick = () => {
      closeContextMenu();
    };

    watchEffect(() => {
      if (contextMenu.visible) {
        document.addEventListener("click", handleOutsideClick);
        return;
      }

      document.removeEventListener("click", handleOutsideClick);
    });

    onBeforeUnmount(() => {
      document.removeEventListener("click", handleOutsideClick);
    });
  }

  return {
    closeContextMenu,
    contextMenu,
    isFirstView,
    isLastView,
    openContextMenu,
    selectedTag,
    useContextMenuManager,
  };
}
