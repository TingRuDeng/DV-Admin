import type { LocationQueryRaw } from "vue-router";

export interface SearchItem {
  title: string;
  path: string;
  name?: string;
  icon?: string;
  redirect?: string;
  params?: LocationQueryRaw;
}

export type SearchDirection = "up" | "down";
