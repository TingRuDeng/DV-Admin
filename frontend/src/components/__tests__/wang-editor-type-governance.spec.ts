import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const WANG_EDITOR_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/WangEditor/index.vue"),
  "utf8"
);

describe("WangEditor 编辑器类型治理", () => {
  it("编辑器实例和上传配置不能回退到显式 any", () => {
    expect(WANG_EDITOR_SOURCE).not.toMatch(/handleCreated\s*=\s*\(editor:\s*any\)/);
    expect(WANG_EDITOR_SOURCE).not.toMatch(/\bas any\b/);
  });

  it("编辑器实例和上传配置必须使用 wangEditor 上游类型", () => {
    expect(WANG_EDITOR_SOURCE).toContain("IDomEditor");
    expect(WANG_EDITOR_SOURCE).toContain("IUploadConfig");
    expect(WANG_EDITOR_SOURCE).toContain("shallowRef<IDomEditor>");
  });
});
