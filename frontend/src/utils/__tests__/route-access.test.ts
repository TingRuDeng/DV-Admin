import { describe, expect, it } from "vitest";
import { hasRouteAccess } from "@/utils/route-access";

describe("route access guard", () => {
  it("allows routes without perms or roles constraints", () => {
    const allowed = hasRouteAccess([{ meta: { title: "Dashboard" } }], {
      userPerms: [],
      userRoles: [],
    });
    expect(allowed).toBe(true);
  });

  it("allows when route perms intersects with user perms", () => {
    const allowed = hasRouteAccess(
      [{ meta: { perms: ["system:user:list", "system:user:view"] } }],
      { userPerms: ["system:user:view"], userRoles: [] }
    );
    expect(allowed).toBe(true);
  });

  it("denies when route perms does not intersect with user perms", () => {
    const allowed = hasRouteAccess([{ meta: { perms: ["system:role:list"] } }], {
      userPerms: ["system:user:view"],
      userRoles: [],
    });
    expect(allowed).toBe(false);
  });

  it("allows when route roles intersects with user roles", () => {
    const allowed = hasRouteAccess([{ meta: { roles: ["admin", "operator"] } }], {
      userPerms: [],
      userRoles: ["operator"],
    });
    expect(allowed).toBe(true);
  });

  it("denies when route roles does not intersect with user roles", () => {
    const allowed = hasRouteAccess([{ meta: { roles: ["admin"] } }], {
      userPerms: [],
      userRoles: ["visitor"],
    });
    expect(allowed).toBe(false);
  });

  it("requires every matched record constraint to pass", () => {
    const allowed = hasRouteAccess(
      [{ meta: { perms: ["system:user:list"] } }, { meta: { roles: ["admin"] } }],
      { userPerms: ["system:user:list"], userRoles: ["visitor"] }
    );
    expect(allowed).toBe(false);
  });

  it("allows super role to bypass route constraints", () => {
    const allowed = hasRouteAccess(
      [{ meta: { perms: ["system:secret:view"], roles: ["admin"] } }],
      { userPerms: [], userRoles: ["ROOT"] }
    );
    expect(allowed).toBe(true);
  });
});
