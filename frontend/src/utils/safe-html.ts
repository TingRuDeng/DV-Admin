const BLOCKED_TAGS = new Set([
  "script",
  "style",
  "iframe",
  "object",
  "embed",
  "link",
  "meta",
  "base",
  "form",
  "input",
  "button",
  "textarea",
  "select",
]);

const ALLOWED_TAGS = new Set([
  "a",
  "b",
  "blockquote",
  "br",
  "code",
  "del",
  "div",
  "em",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "hr",
  "i",
  "img",
  "li",
  "ol",
  "p",
  "pre",
  "s",
  "span",
  "strong",
  "table",
  "tbody",
  "td",
  "th",
  "thead",
  "tr",
  "u",
  "ul",
]);

const GLOBAL_ATTRS = new Set(["class", "title"]);
const TAG_ATTRS: Record<string, Set<string>> = {
  a: new Set(["href", "target", "rel"]),
  img: new Set(["src", "alt", "width", "height"]),
  td: new Set(["colspan", "rowspan"]),
  th: new Set(["colspan", "rowspan"]),
};

const URL_ATTRS = new Set(["href", "src"]);
const SAFE_PROTOCOLS = new Set(["http:", "https:", "mailto:", "tel:"]);

// SSR 或非浏览器环境没有 DOMParser，只能退化为纯文本转义，避免原样输出 HTML。
function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// 仅允许常见安全协议和相对地址，避免 javascript: 等协议进入 href/src。
function isSafeUrl(value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return false;
  }

  if (trimmed.startsWith("/") || trimmed.startsWith("./") || trimmed.startsWith("../")) {
    return true;
  }

  try {
    const url = new URL(trimmed, window.location.origin);
    return SAFE_PROTOCOLS.has(url.protocol);
  } catch {
    return false;
  }
}

// 白名单属性之外全部移除，尤其是事件属性和 style，降低富文本 XSS 面。
function isAllowedAttribute(tagName: string, attrName: string) {
  if (attrName.startsWith("on") || attrName === "style") {
    return false;
  }

  return GLOBAL_ATTRS.has(attrName) || TAG_ATTRS[tagName]?.has(attrName) === true;
}

// 属性净化在标签确认安全后执行，保留编辑器常用的链接、图片和表格属性。
function sanitizeAttributes(element: Element) {
  const tagName = element.tagName.toLowerCase();

  Array.from(element.attributes).forEach((attr) => {
    const attrName = attr.name.toLowerCase();
    const attrValue = attr.value;

    if (!isAllowedAttribute(tagName, attrName)) {
      element.removeAttribute(attr.name);
      return;
    }

    if (URL_ATTRS.has(attrName) && !isSafeUrl(attrValue)) {
      element.removeAttribute(attr.name);
      return;
    }

    if (attrName === "target" && !["_blank", "_self"].includes(attrValue)) {
      element.removeAttribute(attr.name);
      return;
    }
  });

  if (tagName === "a" && element.getAttribute("target") === "_blank") {
    element.setAttribute("rel", "noopener noreferrer");
  }
}

// 非白名单但非高危标签只展开内容，尽量保留可读文本而不是整段丢弃。
function unwrapElement(element: Element) {
  const fragment = document.createDocumentFragment();
  while (element.firstChild) {
    fragment.appendChild(element.firstChild);
  }
  element.replaceWith(fragment);
}

// 先递归净化子节点，再处理当前节点，避免未知包装标签包住危险子节点。
function sanitizeNode(node: ChildNode) {
  if (node.nodeType !== Node.ELEMENT_NODE) {
    return;
  }

  const element = node as Element;
  const tagName = element.tagName.toLowerCase();

  if (BLOCKED_TAGS.has(tagName)) {
    element.remove();
    return;
  }

  Array.from(node.childNodes).forEach(sanitizeNode);

  if (!ALLOWED_TAGS.has(tagName)) {
    unwrapElement(element);
    return;
  }

  sanitizeAttributes(element);
}

// 对后端富文本做前端最后一道白名单净化，所有 v-html 入口必须使用该函数。
export function sanitizeHtml(value: unknown) {
  const rawHtml = typeof value === "string" ? value : "";
  if (!rawHtml) {
    return "";
  }

  if (typeof window === "undefined" || typeof document === "undefined") {
    return escapeHtml(rawHtml);
  }

  const template = document.createElement("template");
  template.innerHTML = rawHtml;
  Array.from(template.content.childNodes).forEach(sanitizeNode);
  return template.innerHTML;
}
