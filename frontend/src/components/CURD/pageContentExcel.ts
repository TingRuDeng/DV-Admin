import ExcelJS from "exceljs";
import type { IObject } from "./types";

export const READ_XLSX_FILE_ERROR = "读取文件失败";

export interface PageContentExcelColumn {
  header: string;
  key: string;
}

export interface WriteXlsxBufferOptions {
  sheetname: string;
  columns: PageContentExcelColumn[];
  rows: IObject[];
}

const XLSX_MIME_TYPE =
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8";

export function saveXlsx(fileData: BlobPart, fileName: string) {
  const blob = new Blob([fileData], { type: XLSX_MIME_TYPE });
  const downloadUrl = window.URL.createObjectURL(blob);

  const downloadLink = document.createElement("a");
  downloadLink.href = downloadUrl;
  downloadLink.download = fileName;

  document.body.appendChild(downloadLink);
  downloadLink.click();

  document.body.removeChild(downloadLink);
  window.URL.revokeObjectURL(downloadUrl);
}

export async function writeXlsxBuffer(options: WriteXlsxBufferOptions) {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet(options.sheetname);
  worksheet.columns = options.columns;
  worksheet.addRows(options.rows);

  return workbook.xlsx.writeBuffer();
}

export function readXlsxRows(file: File): Promise<IObject[]> {
  return new Promise((resolve, reject) => {
    const fileReader = new FileReader();

    fileReader.onerror = () => reject(new Error(READ_XLSX_FILE_ERROR));
    fileReader.onload = (event) => {
      if (event.target === null || event.target.result === null) {
        reject(new Error(READ_XLSX_FILE_ERROR));
        return;
      }

      parseXlsxRows(event.target.result as ArrayBuffer)
        .then(resolve)
        .catch(reject);
    };
    fileReader.readAsArrayBuffer(file);
  });
}

async function parseXlsxRows(buffer: ArrayBuffer) {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.load(buffer);

  const worksheet = workbook.getWorksheet(1);
  if (!worksheet) {
    return [];
  }

  const fields: unknown[] = [];
  worksheet.getRow(1).eachCell((cell) => {
    fields.push(cell.value);
  });

  const rows: IObject[] = [];
  for (let rowNumber = 2; rowNumber <= worksheet.rowCount; rowNumber++) {
    const row = worksheet.getRow(rowNumber);
    const rowData: IObject = {};

    row.eachCell((cell, colNumber) => {
      const field = fields[colNumber - 1];
      if (typeof field === "string" && field !== "") {
        rowData[field] = cell.value;
      }
    });
    rows.push(rowData);
  }

  return rows;
}
