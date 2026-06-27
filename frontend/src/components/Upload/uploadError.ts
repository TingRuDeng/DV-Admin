const DEFAULT_UPLOAD_ERROR_MESSAGE = "上传失败";

interface UploadErrorLike {
  message?: unknown;
}

// 从未知上传错误中提取可展示文案，避免组件直接依赖 any.message。
export function getUploadErrorMessage(error: unknown) {
  if (error instanceof Error && error.message) {
    return error.message;
  }

  if (typeof error === "object" && error !== null && "message" in error) {
    const message = (error as UploadErrorLike).message;
    if (typeof message === "string" && message) {
      return message;
    }
  }

  return DEFAULT_UPLOAD_ERROR_MESSAGE;
}
