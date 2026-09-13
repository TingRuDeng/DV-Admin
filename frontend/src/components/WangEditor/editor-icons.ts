import { h, render, type Component } from "vue";
import {
  AlignCenter,
  AlignJustify,
  AlignLeft,
  AlignRight,
  Bold,
  ChevronDown,
  Code,
  Columns3,
  ExternalLink,
  Heading1,
  Heading2,
  Heading3,
  Highlighter,
  Image,
  Italic,
  Link,
  List,
  ListOrdered,
  ListTodo,
  Maximize2,
  Minimize2,
  MoreHorizontal,
  Palette,
  Pencil,
  Quote,
  Redo2,
  RemoveFormatting,
  Rows3,
  Table,
  Trash2,
  Underline,
  Undo2,
  Unlink,
  Upload,
  Video,
  X,
  Strikethrough,
} from "@lucide/vue";

const menuIcons: Record<string, Component> = {
  blockquote: Quote,
  header1: Heading1,
  header2: Heading2,
  header3: Heading3,
  bold: Bold,
  underline: Underline,
  italic: Italic,
  through: Strikethrough,
  color: Palette,
  bgColor: Highlighter,
  clearStyle: RemoveFormatting,
  bulletedList: List,
  numberedList: ListOrdered,
  todo: ListTodo,
  justifyLeft: AlignLeft,
  justifyRight: AlignRight,
  justifyCenter: AlignCenter,
  justifyJustify: AlignJustify,
  insertLink: Link,
  editLink: Pencil,
  unLink: Unlink,
  viewLink: ExternalLink,
  "group-image": Image,
  insertImage: Image,
  uploadImage: Upload,
  deleteImage: Trash2,
  editImage: Pencil,
  viewImageLink: ExternalLink,
  insertVideo: Video,
  uploadVideo: Upload,
  deleteVideo: Trash2,
  editVideoSize: Maximize2,
  editVideoSrc: Link,
  insertTable: Table,
  deleteTable: Trash2,
  insertTableRow: Rows3,
  deleteTableRow: Rows3,
  insertTableCol: Columns3,
  deleteTableCol: Columns3,
  tableHeader: Table,
  tableFullWidth: Maximize2,
  mergeTableCell: Table,
  splitTableCell: Table,
  setTableProperty: Table,
  setTableCellProperty: Table,
  codeBlock: Code,
  undo: Undo2,
  redo: Redo2,
  fullScreen: Maximize2,
};

/**
 * wangEditor exposes menu icons but strips their SVG styles and has no icon
 * renderer hook for dropdown arrows or hoverbars. Adapt only its UI surfaces;
 * the editable document and the menu buttons/listeners stay owned by the editor.
 */
export function bindEditorIcons(
  root: HTMLElement,
  isFullScreen: () => boolean = () => false,
  menuLabel: (key: string) => string | undefined = () => undefined
) {
  const templates = new Map<Component, SVGSVGElement>();

  function createIcon(icon: Component) {
    let template = templates.get(icon);
    if (!template) {
      const container = document.createElement("div");
      render(h(icon, { size: 18, strokeWidth: 1.8, "aria-hidden": true }), container);
      template = container.querySelector("svg")!.cloneNode(true) as SVGSVGElement;
      template.dataset.editorLucide = "true";
      template.style.fill = "none";
      render(null, container);
      templates.set(icon, template);
    }
    return template.cloneNode(true) as SVGSVGElement;
  }

  function replaceIcons() {
    const icons = root.querySelectorAll<SVGSVGElement>(
      ".w-e-bar svg, .w-e-hover-bar svg, .w-e-modal svg, .w-e-droppanel svg"
    );
    for (const svg of Array.from(icons)) {
      if (svg.closest("[data-slate-editor]")) continue;
      const button = svg.closest<HTMLButtonElement>("button");
      const key = button?.dataset.menuKey;
      const label = (key && menuLabel(key)) || button?.getAttribute("data-tooltip")?.split("\n")[0];
      if (label) button?.setAttribute("aria-label", label);
      if (svg.dataset.editorLucide) {
        if (key !== "fullScreen") continue;
        const expectedClass = isFullScreen() ? "lucide-minimize-2" : "lucide-maximize-2";
        if (svg.classList.contains(expectedClass)) continue;
      }
      const isArrow = button && Array.from(button.querySelectorAll("svg")).indexOf(svg) > 0;
      const icon = isArrow
        ? ChevronDown
        : key === "fullScreen" && isFullScreen()
          ? Minimize2
          : key
            ? (menuIcons[key] ?? (key.startsWith("group-") ? MoreHorizontal : ChevronDown))
            : X;
      svg.replaceWith(createIcon(icon));
    }
  }

  // Menus, hoverbars and fullscreen icons are rebuilt by the editor on demand.
  const observer = new MutationObserver(replaceIcons);
  observer.observe(root, { childList: true, subtree: true });
  replaceIcons();
  return {
    refresh: replaceIcons,
    dispose() {
      observer.disconnect();
      templates.clear();
    },
  };
}
