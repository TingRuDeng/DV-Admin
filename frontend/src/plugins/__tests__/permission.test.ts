import type { RouteLocationNormalized, RouteLocationNormalizedLoaded } from "vue-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  addRoute: vi.fn(),
  afterEach: vi.fn(),
  beforeEach: vi.fn(),
  done: vi.fn(),
  error: vi.fn(),
  generateRoutes: vi.fn(),
  getUserInfo: vi.fn(),
  hasRouteAccess: vi.fn(),
  isLoggedIn: vi.fn(),
  resetAllState: vi.fn(),
  start: vi.fn(),
  permissionStore: {
    isRouteGenerated: true,
  },
  userInfo: {
    perms: ["system:user:list"],
    roles: ["admin"],
  },
}));

vi.mock("@/router", () => ({
  default: {
    addRoute: mocks.addRoute,
    afterEach: mocks.afterEach,
    beforeEach: mocks.beforeEach,
  },
}));

vi.mock("@/store", () => ({
  usePermissionStore: () => ({
    ...mocks.permissionStore,
    generateRoutes: mocks.generateRoutes,
  }),
  useUserStore: () => ({
    getUserInfo: mocks.getUserInfo,
    isLoggedIn: mocks.isLoggedIn,
    resetAllState: mocks.resetAllState,
    userInfo: mocks.userInfo,
  }),
}));

vi.mock("@/utils/nprogress", () => ({
  default: {
    done: mocks.done,
    start: mocks.start,
  },
}));

vi.mock("@/utils/logger", () => ({
  createLogger: () => ({
    error: mocks.error,
  }),
}));

vi.mock("@/utils/route-access", () => ({
  hasRouteAccess: mocks.hasRouteAccess,
}));

import { setupPermission } from "@/plugins/permission";

type RegisteredGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalizedLoaded
) => unknown;

function createRoute(overrides: Partial<RouteLocationNormalized> = {}): RouteLocationNormalized {
  return {
    fullPath: "/dashboard",
    hash: "",
    matched: [{ meta: {} }],
    meta: {},
    name: "Dashboard",
    params: {},
    path: "/dashboard",
    query: {},
    redirectedFrom: undefined,
    ...overrides,
  } as RouteLocationNormalized;
}

function registerGuard(): RegisteredGuard {
  setupPermission();
  return mocks.beforeEach.mock.calls[0][0] as RegisteredGuard;
}

describe("permission navigation guard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.permissionStore.isRouteGenerated = true;
    mocks.userInfo.perms = ["system:user:list"];
    mocks.userInfo.roles = ["admin"];
    mocks.generateRoutes.mockResolvedValue([]);
    mocks.hasRouteAccess.mockReturnValue(true);
    mocks.isLoggedIn.mockReturnValue(true);
  });

  it("uses the return-based guard API instead of the deprecated next callback", () => {
    const guard = registerGuard();

    expect(guard.length).toBeLessThan(3);
  });

  it.each(["/login", "/401", "/403", "/404"])(
    "allows unauthenticated access to %s",
    async (path) => {
      mocks.isLoggedIn.mockReturnValue(false);
      const guard = registerGuard();

      await expect(guard(createRoute({ fullPath: path, path }), createRoute())).resolves.toBe(
        undefined
      );
    }
  );

  it("redirects unauthenticated users and preserves the requested location", async () => {
    mocks.isLoggedIn.mockReturnValue(false);
    const guard = registerGuard();

    await expect(
      guard(createRoute({ fullPath: "/system/users?page=2", path: "/system/users" }), createRoute())
    ).resolves.toBe("/login?redirect=%2Fsystem%2Fusers%3Fpage%3D2");
    expect(mocks.done).toHaveBeenCalledOnce();
  });

  it("injects dynamic routes before retrying the current navigation", async () => {
    mocks.permissionStore.isRouteGenerated = false;
    const dynamicRoute = { name: "System", path: "/system" };
    mocks.generateRoutes.mockResolvedValue([dynamicRoute]);
    const guard = registerGuard();
    const target = createRoute({ fullPath: "/system", matched: [], path: "/system" });

    const result = await guard(target, createRoute());

    expect(mocks.addRoute).toHaveBeenCalledWith(dynamicRoute);
    expect(result).toMatchObject({ fullPath: "/system", path: "/system", replace: true });
  });

  it("redirects unmatched and unauthorized routes through return values", async () => {
    const guard = registerGuard();

    await expect(guard(createRoute({ matched: [] }), createRoute())).resolves.toBe("/404");

    mocks.hasRouteAccess.mockReturnValue(false);
    await expect(guard(createRoute(), createRoute())).resolves.toBe("/403");
  });

  it("keeps dynamic titles and completes successful navigation", async () => {
    const guard = registerGuard();
    const target = createRoute({ query: { title: "订单详情" } });

    await expect(guard(target, createRoute())).resolves.toBe(undefined);
    expect(target.meta.title).toBe("订单详情");
  });

  it("resets state and returns to login when route generation fails", async () => {
    mocks.permissionStore.isRouteGenerated = false;
    mocks.generateRoutes.mockRejectedValue(new Error("route failure"));
    const guard = registerGuard();

    await expect(guard(createRoute(), createRoute())).resolves.toBe("/login");
    expect(mocks.error).toHaveBeenCalledOnce();
    expect(mocks.resetAllState).toHaveBeenCalledOnce();
    expect(mocks.done).toHaveBeenCalledOnce();
  });
});
