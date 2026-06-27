import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { getUploadErrorMessage } from "@/components/Upload/uploadError";

const UPLOAD_COMPONENT_FILES = [
  "src/components/Upload/SingleImageUpload.vue",
  "src/components/Upload/FileUpload.vue",
  "src/components/Upload/MultiImageUpload.vue",
];

describe("上传错误类型治理", () => {
  it("上传失败回调不能回退到显式 any", () => {
    const sources = UPLOAD_COMPONENT_FILES.map((file) =>
      readFileSync(resolve(process.cwd(), file), "utf8")
    ).join("\n");

    expect(sources).not.toMatch(/\b_?error:\s*any\b/);
    expect(sources).toMatch(/\b_?error:\s*unknown\b/);
  });

  it("未知上传错误只在窄化后读取 message", () => {
    expect(getUploadErrorMessage(new Error("网络异常"))).toBe("网络异常");
    expect(getUploadErrorMessage({ message: "文件过大" })).toBe("文件过大");
    expect(getUploadErrorMessage({ message: 500 })).toBe("上传失败");
    expect(getUploadErrorMessage(null)).toBe("上传失败");
  });
});
