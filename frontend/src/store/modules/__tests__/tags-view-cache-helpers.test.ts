import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  appendCachedTagView,
  createTagsViewChangeResult,
  keepOnlyCachedTagView,
  removeCachedTagView,
  syncUpdatedCachedTagView,
} from "../tags-view-cache-helpers";

function createTag(overrides: Partial<TagView> = {}): TagView {
  return {
    name: "UserManagement",
    title: "用户管理",
    path: "/system/users",
    fullPath: "/system/users",
    cacheKey: "system-users",
    keepAlive: true,
    ...overrides,
  };
}

describe("tags view cache helpers", () => {
  it("appends keepAlive tag cache keys once", () => {
    const tag = createTag();

    expect(appendCachedTagView([], tag)).toEqual(["system-users"]);
    expect(appendCachedTagView(["system-users"], tag)).toEqual(["system-users"]);
    expect(appendCachedTagView([], createTag({ keepAlive: false }))).toEqual([]);
  });

  it("removes and keeps cache keys by tag", () => {
    const tag = createTag();
    const cachedViews = ["dashboard", "system-users", "system-roles"];

    expect(removeCachedTagView(cachedViews, tag)).toEqual(["dashboard", "system-roles"]);
    expect(keepOnlyCachedTagView(cachedViews, tag)).toEqual(["system-users"]);
    expect(keepOnlyCachedTagView(cachedViews, createTag({ cacheKey: "missing" }))).toEqual([]);
  });

  it("syncs cache keys when a visited tag changes", () => {
    const previousTag = createTag({ cacheKey: "system-users-page-1" });
    const nextTag = createTag({ cacheKey: "system-users-page-2" });

    expect(
      syncUpdatedCachedTagView(["dashboard", "system-users-page-1"], previousTag, nextTag)
    ).toEqual(["dashboard", "system-users-page-2"]);

    expect(
      syncUpdatedCachedTagView(["dashboard", "system-users-page-2"], nextTag, {
        ...nextTag,
        keepAlive: false,
      })
    ).toEqual(["dashboard"]);
  });

  it("creates immutable change snapshots", () => {
    const tag = createTag();
    const cachedViews = ["system-users"];
    const result = createTagsViewChangeResult([tag], cachedViews);

    cachedViews.push("system-roles");

    expect(result).toEqual({
      visitedViews: [tag],
      cachedViews: ["system-users"],
    });
  });

  it("keeps tags view store below the file size hard limit", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/store/modules/tags-view-store.ts"),
      "utf8"
    );

    expect(source.split("\n").length).toBeLessThan(300);
  });
});
