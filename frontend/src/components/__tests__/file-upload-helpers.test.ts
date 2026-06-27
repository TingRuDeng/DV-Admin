import type { UploadFile, UploadFiles } from "element-plus";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  collectSuccessfulFileInfos,
  createUploadedFiles,
  isUploadBatchFinished,
  removeUploadFilesByUid,
  resolveFileDeletePath,
  type FileModel,
  type UploadedFile,
} from "@/components/Upload/fileUploadHelpers";

function createUploadFile(overrides: Partial<UploadFile> = {}): UploadFile {
  return {
    name: "合同.pdf",
    status: "success",
    uid: 1,
    ...overrides,
  } as UploadFile;
}

describe("file upload helpers", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("maps model files to Element Plus upload display files", () => {
    vi.spyOn(Date, "now").mockReturnValue(1000);
    vi.spyOn(Math, "random").mockReturnValue(0);

    const files: FileModel[] = [
      { name: "合同.pdf", url: "/media/files/contract.pdf", path: "files/1/contract.pdf" },
      { name: "", url: "/media/files/report.xlsx", path: "files/1/report.xlsx" },
    ];

    expect(createUploadedFiles(files)).toEqual([
      {
        name: "合同.pdf",
        url: "/media/files/contract.pdf",
        path: "files/1/contract.pdf",
        status: "success",
        uid: 8192000,
      },
      {
        name: "report.xlsx",
        url: "/media/files/report.xlsx",
        path: "files/1/report.xlsx",
        status: "success",
        uid: 8192000,
      },
    ]);
  });

  it("detects whether an upload batch has finished", () => {
    expect(
      isUploadBatchFinished([
        createUploadFile({ status: "success" }),
        createUploadFile({ status: "fail" }),
      ] as UploadFiles)
    ).toBe(true);

    expect(
      isUploadBatchFinished([
        createUploadFile({ status: "success" }),
        createUploadFile({ status: "uploading" }),
      ] as UploadFiles)
    ).toBe(false);
  });

  it("collects successful upload responses and failed file uids", () => {
    const successFile = createUploadFile({
      uid: 1,
      response: {
        name: "合同.pdf",
        url: "/media/files/contract.pdf",
        path: "files/1/contract.pdf",
      },
    }) as UploadedFile;
    const failedFile = createUploadFile({ uid: 2, status: "fail" }) as UploadedFile;

    const result = collectSuccessfulFileInfos([successFile, failedFile] as UploadFiles);

    expect(result).toEqual({
      fileInfos: [
        {
          name: "合同.pdf",
          url: "/media/files/contract.pdf",
          path: "files/1/contract.pdf",
        },
      ],
      failedUids: [2],
      uploadedPathsByUid: new Map([[1, "files/1/contract.pdf"]]),
    });
    expect(successFile.path).toBeUndefined();
  });

  it("removes failed files by uid", () => {
    const files = [
      createUploadFile({ uid: 1 }) as UploadedFile,
      createUploadFile({ uid: 2 }) as UploadedFile,
    ];

    expect(removeUploadFilesByUid(files, [2]).map((file) => file.uid)).toEqual([1]);
  });

  it("resolves delete path from uploaded file before model fallback", () => {
    const file = createUploadFile({
      url: "/media/files/contract.pdf",
      path: "files/1/current.pdf",
    } as Partial<UploadedFile>) as UploadedFile;
    const modelValue: FileModel[] = [
      { name: "合同.pdf", url: "/media/files/contract.pdf", path: "files/1/model.pdf" },
    ];

    expect(resolveFileDeletePath(file, modelValue)).toBe("files/1/current.pdf");
    expect(resolveFileDeletePath({ ...file, path: undefined }, modelValue)).toBe(
      "files/1/model.pdf"
    );
  });
});
