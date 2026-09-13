import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import zhCn from "../package/zh-cn.json";
import en from "../package/en.json";

function flattenKeys(value: unknown, prefix = ""): string[] {
  if (!value || typeof value !== "object") return prefix ? [prefix] : [];
  return Object.entries(value as Record<string, unknown>).flatMap(([key, child]) =>
    flattenKeys(child, prefix ? `${prefix}.${key}` : key)
  );
}

function collectVueFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = resolve(directory, entry.name);
    return entry.isDirectory() ? collectVueFiles(path) : path.endsWith(".vue") ? [path] : [];
  });
}

describe("system page locale governance", () => {
  it("keeps Chinese and English locale key trees aligned", () => {
    expect(flattenKeys(zhCn).sort()).toEqual(flattenKeys(en).sort());
  });

  it("does not leave Chinese user-facing attributes or template text in system pages", () => {
    const chinese = /[\u4e00-\u9fff]/;
    const userFacing =
      /(?:label|placeholder|title|aria-label|alt)="[^"{}]*[\u4e00-\u9fff]|>\s*[^<{]*[\u4e00-\u9fff][^<]*</;
    const systemViews = resolve(process.cwd(), "src/views/system");

    for (const file of collectVueFiles(systemViews)) {
      const source = readFileSync(file, "utf8")
        .replace(/<!--[\s\S]*?-->/g, "")
        .replace(/<script[\s\S]*?<\/script>/g, "")
        .replace(/<style[\s\S]*?<\/style>/g, "");
      if (chinese.test(source)) {
        expect(source).not.toMatch(userFacing);
      }
    }
  });
});
