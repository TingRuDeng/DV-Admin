import type { UploadFile, UploadFiles } from "element-plus";
import type { FileInfo } from "@/api/file-api";

export type FileModel = Pick<FileInfo, "name" | "url"> & Partial<Pick<FileInfo, "path">>;
export type UploadedFile = UploadFile & { path?: string };

export function createUploadUid() {
  // 与原组件行为保持一致：时间戳左移后追加低位随机数，降低同批次文件 uid 冲突概率。
  return (Date.now() << 13) | Math.floor(Math.random() * 8192);
}

export function getUploadDisplayName(file: FileModel) {
  return file.name ? file.name : file.url?.substring(file.url.lastIndexOf("/") + 1);
}

export function createUploadedFile(file: FileModel): UploadedFile {
  return {
    name: getUploadDisplayName(file),
    url: file.url,
    path: file.path,
    status: "success",
    uid: createUploadUid(),
  } as UploadedFile;
}

export function createUploadedFiles(files: FileModel[]) {
  return files.map((file) => createUploadedFile(file));
}

export function isUploadBatchFinished(files: UploadFiles) {
  return files.every((file) => file.status === "success" || file.status === "fail");
}

export function collectSuccessfulFileInfos(files: UploadFiles) {
  const fileInfos: FileInfo[] = [];
  const failedUids: number[] = [];
  const uploadedPathsByUid = new Map<number, string>();

  files.forEach((file: UploadedFile) => {
    if (file.status !== "success") {
      failedUids.push(file.uid);
      return;
    }

    const response = file.response as FileInfo | undefined;
    if (!response) {
      return;
    }

    uploadedPathsByUid.set(file.uid, response.path);
    fileInfos.push({ name: response.name, url: response.url, path: response.path });
  });

  return { fileInfos, failedUids, uploadedPathsByUid };
}

export function removeUploadFilesByUid(files: UploadedFile[], failedUids: number[]) {
  return files.filter((file) => !failedUids.includes(file.uid));
}

export function resolveFileDeletePath(file: UploadedFile, modelValue: FileModel[]) {
  return file.path ?? modelValue.find((item) => item.url === file.url)?.path;
}
