import ExcelJS from "exceljs";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  READ_XLSX_FILE_ERROR,
  readXlsxRows,
  saveXlsx,
  writeXlsxBuffer,
} from "@/components/CURD/pageContentExcel";

async function createWorkbookFile(rows: Record<string, unknown>[]) {
  const buffer = await writeXlsxBuffer({
    sheetname: "用户",
    columns: [
      { header: "username", key: "username" },
      { header: "status", key: "status" },
    ],
    rows,
  });

  return new File([buffer], "users.xlsx");
}

describe("PageContent Excel 文件处理", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("写入 Excel buffer 时保留列头和行数据", async () => {
    const buffer = await writeXlsxBuffer({
      sheetname: "用户",
      columns: [
        { header: "username", key: "username" },
        { header: "status", key: "status" },
      ],
      rows: [{ username: "admin", status: "enabled" }],
    });

    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(buffer);
    const worksheet = workbook.getWorksheet(1);

    expect(worksheet?.getCell("A1").value).toBe("username");
    expect(worksheet?.getCell("B1").value).toBe("status");
    expect(worksheet?.getCell("A2").value).toBe("admin");
    expect(worksheet?.getCell("B2").value).toBe("enabled");
  });

  it("读取 Excel 文件时按首行标题解析业务行", async () => {
    const file = await createWorkbookFile([{ username: "visitor", status: "disabled" }]);

    await expect(readXlsxRows(file)).resolves.toEqual([
      { username: "visitor", status: "disabled" },
    ]);
  });

  it("读取只有标题行的 Excel 文件时返回空数组", async () => {
    const file = await createWorkbookFile([]);

    await expect(readXlsxRows(file)).resolves.toEqual([]);
  });

  it("文件读取失败时暴露明确错误", async () => {
    const originalFileReader = window.FileReader;
    class BrokenFileReader extends EventTarget {
      onerror: (() => void) | null = null;
      onload: ((event: ProgressEvent<FileReader>) => void) | null = null;

      readAsArrayBuffer() {
        this.onerror?.();
      }
    }

    vi.stubGlobal("FileReader", BrokenFileReader);

    await expect(readXlsxRows(new File(["broken"], "broken.xlsx"))).rejects.toThrow(
      READ_XLSX_FILE_ERROR
    );

    vi.stubGlobal("FileReader", originalFileReader);
  });

  it("保存 Excel 文件时创建临时下载链接并释放 URL", () => {
    const appendChild = vi.spyOn(document.body, "appendChild");
    const removeChild = vi.spyOn(document.body, "removeChild");
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    const createObjectURL = vi
      .spyOn(window.URL, "createObjectURL")
      .mockReturnValue("blob:page-content-export");
    const revokeObjectURL = vi.spyOn(window.URL, "revokeObjectURL").mockImplementation(() => {});

    saveXlsx("file-data", "users.xlsx");

    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(appendChild).toHaveBeenCalledTimes(1);
    expect(click).toHaveBeenCalledTimes(1);
    expect(removeChild).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:page-content-export");
  });
});
