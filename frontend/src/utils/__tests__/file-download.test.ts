import { afterEach, describe, expect, it, vi } from "vitest";
import { downloadEncodedFile } from "@/utils/file-download";

describe("downloadEncodedFile", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("decodes the response and revokes the object URL", async () => {
    const createObjectURL = vi.spyOn(window.URL, "createObjectURL").mockReturnValue("blob:test");
    const revokeObjectURL = vi.spyOn(window.URL, "revokeObjectURL").mockImplementation(() => {});
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    downloadEncodedFile({
      filename: "users.csv",
      content: "AQID",
      contentType: "text/csv;charset=utf-8",
    });

    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:test");
    const blob = createObjectURL.mock.calls[0]?.[0];
    expect(blob).toBeInstanceOf(Blob);
    if (!(blob instanceof Blob)) {
      throw new TypeError("createObjectURL should receive a Blob");
    }
    expect(Array.from(new Uint8Array(await blob.arrayBuffer()))).toEqual([1, 2, 3]);
  });
});
