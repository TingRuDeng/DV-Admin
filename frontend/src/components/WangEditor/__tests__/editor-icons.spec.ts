import { afterEach, describe, expect, it, vi } from "vitest";
import { bindEditorIcons } from "../editor-icons";

let icons: ReturnType<typeof bindEditorIcons> | undefined;
afterEach(() => {
  icons?.dispose();
  document.body.innerHTML = "";
});

describe("editor icon boundary", () => {
  it("replaces late toolbar icons without changing document content or command listeners", async () => {
    const root = document.createElement("div");
    root.innerHTML =
      '<div class="w-e-textarea" data-slate-editor><div class="w-e-bar"><svg data-content="original"></svg></div></div><div class="w-e-bar" data-toolbar></div>';
    document.body.append(root);
    const content = root.querySelector(".w-e-textarea")!.innerHTML;
    icons = bindEditorIcons(root);
    const button = document.createElement("button");
    button.dataset.menuKey = "bold";
    button.setAttribute("data-tooltip", "Bold\nctrl+b");
    button.innerHTML = "<svg></svg>";
    const command = vi.fn();
    button.addEventListener("click", command);
    root.querySelector("[data-toolbar]")!.append(button);
    await vi.waitFor(() => expect(button.querySelector(".lucide-bold")).not.toBeNull());
    button.click();
    expect(command).toHaveBeenCalledOnce();
    expect(button.getAttribute("aria-label")).toBe("Bold");
    expect(root.querySelector(".w-e-textarea")!.innerHTML).toBe(content);
  });

  it("names grouped controls while preserving their dropdown arrow", () => {
    const root = document.createElement("div");
    root.innerHTML =
      '<div class="w-e-bar"><button data-menu-key="group-image"><svg></svg><svg></svg></button></div>';
    icons = bindEditorIcons(
      root,
      () => false,
      (key) => (key === "group-image" ? "Images" : undefined)
    );
    expect(root.querySelector("button")?.getAttribute("aria-label")).toBe("Images");
    expect(root.querySelector(".lucide-image")).not.toBeNull();
    expect(root.querySelector(".lucide-chevron-down")).not.toBeNull();
  });

  it("adapts icons rebuilt after a fullscreen toggle", async () => {
    const root = document.createElement("div");
    root.innerHTML =
      '<div class="w-e-bar"><button data-menu-key="fullScreen"><svg></svg></button></div>';
    let fullscreen = false;
    icons = bindEditorIcons(root, () => fullscreen);
    expect(root.querySelector(".lucide-maximize-2")).not.toBeNull();
    fullscreen = true;
    root.querySelector("button")!.innerHTML = "<svg></svg>";
    await vi.waitFor(() => expect(root.querySelector(".lucide-minimize-2")).not.toBeNull());
    // The editor delays its exit state until after rebuilding the button.
    fullscreen = false;
    icons.refresh();
    expect(root.querySelector(".lucide-maximize-2")).not.toBeNull();
  });
});
