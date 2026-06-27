import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const CURD_ROOT = resolve(process.cwd(), "src/components/CURD");
const TYPES_SOURCE = readFileSync(resolve(CURD_ROOT, "types.ts"), "utf8");
const PAGE_SEARCH_SOURCE = readFileSync(resolve(CURD_ROOT, "PageSearch.vue"), "utf8");
const PAGE_MODAL_SOURCE = readFileSync(resolve(CURD_ROOT, "PageModal.vue"), "utf8");

describe("CURD component map type governance", () => {
  it("keeps component maps away from explicit any", () => {
    const sources = [PAGE_SEARCH_SOURCE, PAGE_MODAL_SOURCE].join("\n");

    expect(sources).not.toMatch(/Map<[^>]+,\s*any>/);
    expect(sources).not.toMatch(/@ts-ignore/);
  });

  it("keeps shared component map types available for search and modal forms", () => {
    expect(TYPES_SOURCE).toContain("export type ICurdComponentMapValue");
    expect(TYPES_SOURCE).toContain("export type ICurdComponentMap");
    expect(TYPES_SOURCE).toContain("export type IOptionComponentType");
  });
});
