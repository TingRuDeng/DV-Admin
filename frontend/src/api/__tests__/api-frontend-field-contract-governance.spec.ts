import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const FRONTEND_FIELD_CONTRACT_FILE = "../scripts/api_frontend_field_contracts.py";
const REQUIRED_CONTRACT_SNIPPETS = [
  "iter_api_frontend_field_contracts",
  "iter_frontend_field_contract_exempt_endpoints",
  "required_fields",
  "logs_page_type",
  "auth_login",
  "files_upload",
];

describe("api frontend field contract governance", () => {
  it("keeps frontend API field contracts registered", () => {
    const source = readFileSync(resolve(process.cwd(), FRONTEND_FIELD_CONTRACT_FILE), "utf8");

    for (const snippet of REQUIRED_CONTRACT_SNIPPETS) {
      expect(source).toContain(snippet);
    }
  });
});
