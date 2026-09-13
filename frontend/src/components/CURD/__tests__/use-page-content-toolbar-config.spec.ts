import { describe, expect, it } from "vitest";
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
import { normalizeToolbarAttrs } from "@/components/CURD/usePageContentToolbarConfig";

describe("normalizeToolbarAttrs", () => {
  it("converts data-driven string icon names to Lucide components", () => {
    const attrs = normalizeToolbarAttrs({ icon: "refresh-right", circle: true });

    expect(attrs.icon).toBe(resolveAppIcon("refresh-right"));
    expect(attrs.circle).toBe(true);
  });

  it("preserves an already resolved icon component", () => {
    const icon = resolveAppIcon("search");
    const attrs = normalizeToolbarAttrs({ icon });

    expect(attrs.icon).toBe(icon);
  });
});
