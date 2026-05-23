import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("profile style migration", () => {
  it("uses PageShell and semantic panels without glass-panel classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/profile/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProfileSidebar");
    expect(source).toContain("<ProfileInfoPanel");
    expect(source).toContain("<ProfileSecurityPanel");
    expect(source).toContain("<ProfileEditDialog");
    expect(source).not.toContain("glass-panel");
  });

  it("keeps Profile index as the orchestration surface", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/profile/index.vue"), "utf8");

    expect(source).not.toContain("<el-descriptions");
    expect(source).not.toContain("<ProDialog");
    expect(source).not.toContain("mobileBinding");
    expect(source).not.toContain("emailBinding");
    expect(source).not.toContain("handleSendMobileCode");
    expect(source).not.toContain("handleSendEmailCode");
  });
});
