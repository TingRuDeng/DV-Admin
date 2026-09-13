import { i18nChangeLanguage } from "@wangeditor-next/editor";

let currentLanguage: string | undefined;

export function syncEditorLanguage(locale: string) {
  const language = locale === "en" ? "en" : "zh-CN";
  // wangEditor shares one language across instances. Repeating this call rebuilds
  // every toolbar and clears hoverbar selections, including in other editors.
  if (language === currentLanguage) return;
  i18nChangeLanguage(language);
  currentLanguage = language;
}
