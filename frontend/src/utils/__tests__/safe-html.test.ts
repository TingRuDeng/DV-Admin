import { describe, expect, it } from "vitest";
import { sanitizeHtml } from "@/utils/safe-html";

describe("sanitizeHtml", () => {
  it("removes script tags and event attributes", () => {
    const html = sanitizeHtml(`<p onclick="alert(1)">正文</p><script>alert(1)</script>`);

    expect(html).toBe("<p>正文</p>");
  });

  it("keeps safe rich text tags and removes style attributes", () => {
    const html = sanitizeHtml(`<p style="color:red"><strong>标题</strong><em>正文</em></p>`);

    expect(html).toBe("<p><strong>标题</strong><em>正文</em></p>");
  });

  it("removes unsafe javascript links", () => {
    const html = sanitizeHtml(`<a href="javascript:alert(1)" target="_blank">打开</a>`);

    expect(html).toBe('<a target="_blank" rel="noopener noreferrer">打开</a>');
  });

  it("keeps safe links and adds noopener for new windows", () => {
    const html = sanitizeHtml(`<a href="https://example.com" target="_blank">官网</a>`);

    expect(html).toBe(
      '<a href="https://example.com" target="_blank" rel="noopener noreferrer">官网</a>'
    );
  });

  it("removes unsafe image urls but keeps alt text", () => {
    const html = sanitizeHtml(`<img src="javascript:alert(1)" alt="公告图" onerror="alert(1)">`);

    expect(html).toBe('<img alt="公告图">');
  });
});
