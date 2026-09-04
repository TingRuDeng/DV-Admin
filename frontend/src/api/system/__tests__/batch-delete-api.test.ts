import { beforeEach, describe, expect, it, vi } from "vitest";

import NoticeAPI from "@/api/system/notice-api";
import RoleAPI from "@/api/system/role-api";
import UserAPI from "@/api/system/user-api";
import request from "@/utils/request";

vi.mock("@/utils/request", () => ({
  default: vi.fn(),
}));

describe("system batch delete APIs", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends normalized JSON IDs and exposes per-item retry endpoints", () => {
    UserAPI.deleteByIds(["12", 13]);
    RoleAPI.deleteByIds(["14"]);
    NoticeAPI.deleteByIds(["15"]);
    UserAPI.retryBatchDelete(["16"]);
    RoleAPI.retryBatchDelete([17]);
    NoticeAPI.retryBatchDelete(["18"]);

    expect(vi.mocked(request).mock.calls).toEqual([
      [
        expect.objectContaining({
          url: "/api/system/users/",
          method: "delete",
          data: { ids: [12, 13] },
        }),
      ],
      [
        expect.objectContaining({
          url: "/api/system/roles/",
          method: "delete",
          data: { ids: [14] },
        }),
      ],
      [
        expect.objectContaining({
          url: "/api/system/notices/",
          method: "delete",
          data: { ids: [15] },
        }),
      ],
      [
        expect.objectContaining({
          url: "/api/system/users/batch-delete/retry/",
          method: "post",
          data: { ids: [16] },
        }),
      ],
      [
        expect.objectContaining({
          url: "/api/system/roles/batch-delete/retry/",
          method: "post",
          data: { ids: [17] },
        }),
      ],
      [
        expect.objectContaining({
          url: "/api/system/notices/batch-delete/retry/",
          method: "post",
          data: { ids: [18] },
        }),
      ],
    ]);
  });

  it("rejects an empty or non-positive batch before making a request", () => {
    expect(() => UserAPI.deleteByIds([])).toThrow("批量删除 ID 列表不能为空");
    expect(() => RoleAPI.deleteByIds([0])).toThrow("批量删除 ID 必须为正整数");
    expect(request).not.toHaveBeenCalled();
  });
});
