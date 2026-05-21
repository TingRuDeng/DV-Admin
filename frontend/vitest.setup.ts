import { useStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, reactive, ref, watch } from "vue";

const testGlobal = globalThis as typeof globalThis & Record<string, unknown>;

// Vitest 直接导入 store 模块时不会经过 AutoImport 插件，这里补齐生产构建中的运行时全局。
Object.assign(testGlobal, {
  computed,
  defineStore,
  reactive,
  ref,
  useRoute: () => ({
    fullPath: "/",
    meta: {},
    name: "Root",
    path: "/",
    query: {},
  }),
  useRouter: () => ({
    push: () => Promise.resolve(),
    replace: () => Promise.resolve(),
  }),
  useStorage,
  watch,
});

// settings.ts 依赖 Vite define 注入的 __APP_INFO__，单测环境需要提供等价只读对象。
Object.defineProperty(testGlobal, "__APP_INFO__", {
  configurable: true,
  value: {
    buildTimestamp: 0,
    pkg: {
      name: "vue3-element-admin",
      version: "0.0.0-test",
    },
  },
});
