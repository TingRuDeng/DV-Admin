import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const FRONTEND_FIELD_CONTRACT_FILE = "../scripts/api_frontend_field_contracts.py";
const REQUIRED_FRONTEND_API_FILES = [
  "frontend/src/api/system/user-api.ts",
  "frontend/src/api/system/role-api.ts",
  "frontend/src/api/system/menu-api.ts",
  "frontend/src/api/system/dept-api.ts",
  "frontend/src/api/system/dict-api.ts",
  "frontend/src/api/system/dict-items-api.ts",
  "frontend/src/api/system/notice-api.ts",
];

describe("api frontend field contract governance", () => {
  it("keeps frontend API field contracts registered", () => {
    const source = readFileSync(resolve(process.cwd(), FRONTEND_FIELD_CONTRACT_FILE), "utf8");

    expect(source).toContain("iter_api_frontend_field_contracts");
    expect(source).toContain("required_fields");

    for (const file of REQUIRED_FRONTEND_API_FILES) {
      expect(source).toContain(file);
    }
  });
});
