import { describe, expect, it } from "vitest";
import { revealRadius, supportsThemeReveal } from "../theme-reveal";

const media = (reduce: boolean) => () => ({ matches: reduce });
const withTransition = { startViewTransition: () => ({}) } as unknown as Document;

describe("theme reveal", () => {
  it("only animates when View Transitions exist and motion is allowed", () => {
    expect(supportsThemeReveal(withTransition, media(false))).toBe(true);
    expect(supportsThemeReveal(withTransition, media(true))).toBe(false);
    expect(supportsThemeReveal({} as Document, media(false))).toBe(false);
    expect(supportsThemeReveal(undefined, media(false))).toBe(false);
  });

  it("grows the circle to the farthest viewport corner", () => {
    expect(revealRadius(0, 0, 300, 400)).toBe(500);
    expect(revealRadius(300, 400, 300, 400)).toBe(500);
    expect(revealRadius(150, 200, 300, 400)).toBe(250);
  });
});
