import { ROLE_ROOT } from "@/constants";

interface RouteMetaLike {
  perms?: string[] | string;
  roles?: string[] | string;
  [key: string]: unknown;
}

interface RouteRecordLike {
  meta?: RouteMetaLike | null;
}

interface RouteAccessOptions {
  userPerms?: string[];
  userRoles?: string[];
  rootRole?: string;
}

function normalizeStringArray(value: unknown): string[] {
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

function hasIntersection(required: string[], owned: string[]): boolean {
  if (required.length === 0) {
    return true;
  }

  if (owned.length === 0) {
    return false;
  }

  return required.some((item) => owned.includes(item));
}

export function hasRouteAccess(
  matchedRecords: RouteRecordLike[],
  options: RouteAccessOptions = {}
): boolean {
  const userPerms = options.userPerms ?? [];
  const userRoles = options.userRoles ?? [];
  const rootRole = options.rootRole ?? ROLE_ROOT;

  if (userRoles.includes(rootRole)) {
    return true;
  }

  return matchedRecords.every((record) => {
    const meta = record.meta ?? {};
    const requiredPerms = normalizeStringArray(meta.perms);
    const requiredRoles = normalizeStringArray(meta.roles);

    return hasIntersection(requiredPerms, userPerms) && hasIntersection(requiredRoles, userRoles);
  });
}
