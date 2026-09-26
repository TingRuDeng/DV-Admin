import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { hasAppIcon, normalizeMenuIconName } from "@/components/AppIcon/icon-map";

interface FixtureRecord {
  model: string;
  fields: { icon?: string | null };
}

// 种子菜单是新环境看到的第一屏，任何一个图标漏配都会在侧栏里显示成问号
function seedMenuIcons() {
  const fixture = JSON.parse(
    readFileSync(resolve(process.cwd(), "../backend/init_data.json"), "utf8")
  ) as FixtureRecord[];
  return [
    ...new Set(
      fixture
        .filter((record) => record.model === "system.permissions" && record.fields.icon)
        .map((record) => record.fields.icon as string)
    ),
  ];
}

describe("menu icon coverage", () => {
  it("normalizes IconSelect prefixes", () => {
    expect(normalizeMenuIconName("el-icon-User")).toBe("User");
    expect(normalizeMenuIconName("i-svg:system")).toBe("system");
    expect(normalizeMenuIconName(undefined)).toBe("menu");
    expect(normalizeMenuIconName("")).toBe("menu");
  });

  it("maps every seeded menu icon to a dedicated icon", () => {
    const icons = seedMenuIcons();
    expect(icons.length).toBeGreaterThan(0);
    const missing = icons.filter((icon) => !hasAppIcon(normalizeMenuIconName(icon)));
    expect(missing).toEqual([]);
  });

  // 页面里写死的 <AppIcon name="..."> 也必须有映射，否则按钮上会出现问号
  it("maps every static AppIcon name used in source", () => {
    const files = (readdirSync(resolve(process.cwd(), "src"), { recursive: true }) as string[])
      .filter((file) => /\.vue$/.test(file) && !file.includes("__tests__"))
      .map((file) => readFileSync(resolve(process.cwd(), "src", file), "utf8"));
    const names = new Set(
      files.flatMap((source) =>
        [...source.matchAll(/<AppIcon[^>]*?\sname="([\w-]+)"/g)].map((match) => match[1])
      )
    );
    expect(names.size).toBeGreaterThan(10);
    expect([...names].filter((name) => !hasAppIcon(name))).toEqual([]);
  });
});
