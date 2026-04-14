import type { RouteMeta } from "vue-router";

interface CacheRouteLike {
  name?: string | symbol | null;
  path?: string;
  fullPath?: string;
  params?: Record<string, unknown>;
  query?: Record<string, unknown>;
  meta?: Partial<RouteMeta> | null;
}

interface CacheTagLike {
  name?: string;
  path?: string;
  fullPath?: string;
  cacheKey?: string;
}

function normalizeName(name: CacheRouteLike["name"] | CacheTagLike["name"]) {
  if (typeof name === "string" && name.length > 0) {
    return name;
  }

  if (typeof name === "symbol") {
    return name.description || name.toString();
  }

  return undefined;
}

function hasRouteParams(params?: Record<string, unknown>) {
  return Boolean(params && Object.keys(params).length > 0);
}

function normalizeCacheKey(value: unknown) {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

function normalizeCacheQueryKeys(value: unknown) {
  if (Array.isArray(value)) {
    return value.filter((item): item is string => typeof item === "string" && item.length > 0);
  }

  return [];
}

function stringifyQueryValue(value: unknown) {
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (value === null) {
    return "null";
  }
  return undefined;
}

function stringifyQueryPart(query: Record<string, unknown>, keys?: string[]) {
  const includeKeys = keys && keys.length > 0 ? keys : Object.keys(query);
  if (includeKeys.length === 0) {
    return "";
  }

  const pairs: string[] = [];

  includeKeys
    .filter((key, index, array) => array.indexOf(key) === index)
    .sort()
    .forEach((key) => {
      const rawValue = query[key];
      if (rawValue === undefined) {
        return;
      }

      if (Array.isArray(rawValue)) {
        const values = rawValue
          .map((item) => stringifyQueryValue(item))
          .filter((item): item is string => item !== undefined)
          .sort();

        values.forEach((value) => {
          pairs.push(`${key}=${value}`);
        });
        return;
      }

      const value = stringifyQueryValue(rawValue);
      if (value !== undefined) {
        pairs.push(`${key}=${value}`);
      }
    });

  return pairs.join("&");
}

function appendQueryCacheSuffix(base: string, querySuffix: string) {
  if (!querySuffix) {
    return base;
  }
  return `${base}::${querySuffix}`;
}

function resolveBaseCacheKey(route: CacheRouteLike) {
  const explicitCacheKey = normalizeCacheKey(route.meta?.cacheKey);
  if (explicitCacheKey) {
    return explicitCacheKey;
  }

  const routeName = normalizeName(route.name);
  if (routeName && !hasRouteParams(route.params)) {
    return routeName;
  }

  return route.fullPath || route.path || routeName || "";
}

export function getRouteCacheKey(route: CacheRouteLike) {
  const baseCacheKey = resolveBaseCacheKey(route);
  const cacheQueryKeys = normalizeCacheQueryKeys(route.meta?.cacheQueryKeys);
  const shouldCacheByQuery = Boolean(route.meta?.cacheByQuery || cacheQueryKeys.length > 0);

  if (!shouldCacheByQuery || !route.query || Object.keys(route.query).length === 0) {
    return baseCacheKey;
  }

  const querySuffix = stringifyQueryPart(route.query, cacheQueryKeys);
  return appendQueryCacheSuffix(baseCacheKey, querySuffix);
}

export function getRouteCacheStrategy(route: CacheRouteLike) {
  const cacheQueryKeys = normalizeCacheQueryKeys(route.meta?.cacheQueryKeys);
  return {
    cacheKey: resolveBaseCacheKey(route),
    cacheByQuery: Boolean(route.meta?.cacheByQuery || cacheQueryKeys.length > 0),
    cacheQueryKeys,
  };
}

export function getRouteRenderKey(route: CacheRouteLike) {
  if (route.meta?.keepAlive) {
    return getRouteCacheKey(route);
  }

  return route.fullPath || route.path || getRouteCacheKey(route);
}

export function getTagCacheKey(tag: CacheTagLike) {
  return (
    normalizeCacheKey(tag.cacheKey) || normalizeName(tag.name) || tag.fullPath || tag.path || ""
  );
}
