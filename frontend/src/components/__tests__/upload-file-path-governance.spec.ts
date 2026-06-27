import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function readSource(path: string) {
  return readFileSync(resolve(process.cwd(), path), "utf-8");
}

describe("upload file path governance", () => {
  it("keeps the file API contract tied to backend relative path", () => {
    const source = readSource("src/api/file-api.ts");

    expect(source).toMatch(/delete\(filePath:\s*string\)/);
    expect(source).not.toContain("delete(filePath?: string)");
    expect(source).toMatch(/export interface FileInfo\s*{[\s\S]*path:\s*string;/);
  });

  it("keeps file upload deletion using the uploaded relative path", () => {
    const source = readSource("src/components/Upload/FileUpload.vue");
    const helperSource = readSource("src/components/Upload/fileUploadHelpers.ts");

    expect(source).not.toContain("handleRemove(file.url!)");
    expect(helperSource).toContain("export type UploadedFile = UploadFile & { path?: string }");
    expect(helperSource).toContain("path: file.path");
    expect(helperSource).toContain("path: response.path");
    expect(helperSource).toContain("resolveFileDeletePath");
    expect(source).toContain("FileAPI.delete(filePath)");
  });

  it("keeps multi image deletion using the uploaded relative path", () => {
    const source = readSource("src/components/Upload/MultiImageUpload.vue");

    expect(source).not.toContain("FileAPI.delete(imageUrl)");
    expect(source).toContain("uploadedFilePaths");
    expect(source).toContain("uploadedFilePaths[fileInfo.url] = fileInfo.path");
    expect(source).toContain("FileAPI.delete(filePath)");
  });
});
