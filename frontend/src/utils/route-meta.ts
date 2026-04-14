import type { RouteMeta } from "vue-router";

type RouteLayout = "left" | "top" | "mix";
type BooleanLike = boolean | number | string | undefined;
type StringArrayLike = string[] | string | undefined;

export interface RouteMetaInput {
  title?: string;
  icon?: string;
  hidden?: BooleanLike;
  alwaysShow?: BooleanLike;
  affix?: BooleanLike;
  keepAlive?: BooleanLike;
  breadcrumb?: BooleanLike;
  activeMenu?: string;
  cacheKey?: string;
  cacheByQuery?: BooleanLike;
  cacheQueryKeys?: StringArrayLike;
  perms?: StringArrayLike;
  permissions?: StringArrayLike;
  roles?: StringArrayLike;
  layout?: RouteLayout | string;
  [key: string]: unknown;
}

interface NormalizeRouteMetaOptions {
  routeName?: string;
}

const truthyValues = new Set(["1", "true", "yes", "on"]);
const falsyValues = new Set(["0", "false", "no", "off"]);
const routeLayouts = new Set<RouteLayout>(["left", "top", "mix"]);

function normalizeBoolean(value: unknown, fallback: boolean) {
  if (value === undefined || value === null || value === "") {
    return fallback;
  }

  if (typeof value === "boolean") {
    return value;
  }

  if (typeof value === "number") {
    return value === 1;
  }

  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();

    if (truthyValues.has(normalized)) {
      return true;
    }

    if (falsyValues.has(normalized)) {
      return false;
    }
  }

  return Boolean(value);
}

function normalizeStringArray(value: unknown) {
  if (Array.isArray(value)) {
    return value.filter((item): item is string => typeof item === "string" && item.length > 0);
  }

  if (typeof value === "string") {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return [];
}

function normalizeLayout(value: unknown): RouteLayout | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  return routeLayouts.has(value as RouteLayout) ? (value as RouteLayout) : undefined;
}

function normalizeString(value: unknown) {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

export function normalizeRouteMeta(
  rawMeta?: unknown,
  options: NormalizeRouteMetaOptions = {}
): RouteMeta {
  const meta =
    rawMeta && typeof rawMeta === "object"
      ? (rawMeta as Record<string, unknown> & RouteMetaInput)
      : {};
  const normalizedTitle = normalizeString(meta.title) ?? options.routeName;

  return {
    ...meta,
    title: normalizedTitle,
    icon: normalizeString(meta.icon),
    hidden: normalizeBoolean(meta.hidden, false),
    alwaysShow: normalizeBoolean(meta.alwaysShow, false),
    affix: normalizeBoolean(meta.affix, false),
    keepAlive: normalizeBoolean(meta.keepAlive, false),
    breadcrumb: meta.breadcrumb === undefined ? true : normalizeBoolean(meta.breadcrumb, false),
    activeMenu: normalizeString(meta.activeMenu),
    cacheKey: normalizeString(meta.cacheKey),
    cacheByQuery: normalizeBoolean(meta.cacheByQuery, false),
    cacheQueryKeys: normalizeStringArray(meta.cacheQueryKeys),
    perms: normalizeStringArray(meta.perms ?? meta.permissions),
    roles: normalizeStringArray(meta.roles),
    layout: normalizeLayout(meta.layout),
  };
}
