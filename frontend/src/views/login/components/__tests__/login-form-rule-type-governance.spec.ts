import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const LOGIN_COMPONENT_ROOT = resolve(__dirname, "..");
const LOGIN_SOURCE = readFileSync(resolve(LOGIN_COMPONENT_ROOT, "Login.vue"), "utf8");
const REGISTER_SOURCE = readFileSync(resolve(LOGIN_COMPONENT_ROOT, "Register.vue"), "utf8");

describe("登录表单规则类型治理", () => {
  it("登录和注册表单规则不能使用显式 any", () => {
    const sources = `${LOGIN_SOURCE}\n${REGISTER_SOURCE}`;

    expect(sources).not.toMatch(/Partial<Record<string,\s*any>>/);
    expect(sources).not.toMatch(/validator:\s*\([^)]*:\s*any/);
  });

  it("登录和注册表单规则使用 Element Plus 表单规则类型", () => {
    expect(LOGIN_SOURCE).toMatch(/const rules: FormRules<LoginFormData>/);
    expect(REGISTER_SOURCE).toMatch(/const registerRules: FormRules<Model>/);
  });

  it("登录组件保持低于文件大小硬限制", () => {
    expect(LOGIN_SOURCE.split("\n").length).toBeLessThan(300);
  });
});
