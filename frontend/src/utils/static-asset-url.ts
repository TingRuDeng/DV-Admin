/** 将后端返回的相对静态资源路径解析为浏览器可直接访问的地址。 */
export function resolveStaticAssetUrl(
  value?: string | null,
  staticBaseUrl: string | undefined = import.meta.env.VITE_APP_STATIC_URL
): string | undefined {
  const assetPath = value?.trim();
  if (!assetPath) {
    return undefined;
  }
  if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(assetPath)) {
    return assetPath;
  }

  const baseUrl = staticBaseUrl?.trim().replace(/\/+$/, "");
  if (!baseUrl) {
    return assetPath;
  }
  return `${baseUrl}/${assetPath.replace(/^\/+/, "")}`;
}
