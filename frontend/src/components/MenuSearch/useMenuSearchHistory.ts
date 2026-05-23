import type { SearchItem } from "./types";

const HISTORY_KEY = "menu_search_history";
const MAX_HISTORY = 5;

function parseHistory(historyStr: string | null): SearchItem[] {
  if (!historyStr) return [];

  try {
    const parsed = JSON.parse(historyStr);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function useMenuSearchHistory() {
  const searchHistory = ref<SearchItem[]>([]);

  function loadSearchHistory() {
    searchHistory.value = parseHistory(localStorage.getItem(HISTORY_KEY));
  }

  function saveSearchHistory() {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value));
  }

  function addToHistory(item: SearchItem) {
    const historyWithoutCurrent = searchHistory.value.filter(
      (historyItem) => historyItem.path !== item.path
    );
    searchHistory.value = [item, ...historyWithoutCurrent].slice(0, MAX_HISTORY);
    saveSearchHistory();
  }

  function removeHistoryItem(index: number) {
    searchHistory.value.splice(index, 1);
    saveSearchHistory();
  }

  function clearHistory() {
    searchHistory.value = [];
    localStorage.removeItem(HISTORY_KEY);
  }

  return {
    addToHistory,
    clearHistory,
    loadSearchHistory,
    removeHistoryItem,
    searchHistory,
  };
}
