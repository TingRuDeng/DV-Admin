import { describe, expect, it } from "vitest";
import { getLoginDefaultCredentials } from "../login-defaults";

describe("login defaults", () => {
  it("returns empty credentials when env defaults are not configured", () => {
    expect(getLoginDefaultCredentials({})).toEqual({
      username: "",
      password: "",
    });
  });

  it("uses explicit env defaults for development convenience", () => {
    expect(
      getLoginDefaultCredentials({
        VITE_LOGIN_DEFAULT_USERNAME: "admin",
        VITE_LOGIN_DEFAULT_PASSWORD: "123456",
      })
    ).toEqual({
      username: "admin",
      password: "123456",
    });
  });
});
