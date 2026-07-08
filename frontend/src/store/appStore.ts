import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ThemeMode, Notification, Scan } from '../types';

// ============================================
// THEME STORE
// ============================================

type ThemeState = {
  mode: ThemeMode;
  setTheme: (mode: ThemeMode) => void;
  toggleTheme: () => void;
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'dark',
      setTheme: (mode) => set({ mode }),
      toggleTheme: () => set({ mode: get().mode === 'dark' ? 'light' : 'dark' }),
    }),
    {
      name: 'osint-fusion-theme',
    }
  )
);

// ============================================
// SIDEBAR STORE
// ============================================

type SidebarState = {
  collapsed: boolean;
  mobileOpen: boolean;
  activeSection: string | null;
  setCollapsed: (collapsed: boolean) => void;
  toggleCollapsed: () => void;
  setMobileOpen: (open: boolean) => void;
  toggleMobile: () => void;
  setActiveSection: (section: string | null) => void;
};

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set, get) => ({
      collapsed: false,
      mobileOpen: false,
      activeSection: null,
      setCollapsed: (collapsed) => set({ collapsed }),
      toggleCollapsed: () => set({ collapsed: !get().collapsed }),
      setMobileOpen: (open) => set({ mobileOpen: open }),
      toggleMobile: () => set({ mobileOpen: !get().mobileOpen }),
      setActiveSection: (section) => set({ activeSection: section }),
    }),
    {
      name: 'osint-fusion-sidebar',
    }
  )
);

// ============================================
// NOTIFICATIONS STORE
// ============================================

type NotificationState = {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
};

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  addNotification: (notification) => {
    const newNotification: Notification = {
      ...notification,
      id: Math.random().toString(36).substring(2, 15),
      timestamp: new Date().toISOString(),
      read: false,
    };
    set({
      notifications: [newNotification, ...get().notifications].slice(0, 100),
      unreadCount: get().unreadCount + 1,
    });
  },
  markAsRead: (id) => {
    const notifications = get().notifications.map((n) =>
      n.id === id ? { ...n, read: true } : n
    );
    const unreadCount = notifications.filter((n) => !n.read).length;
    set({ notifications, unreadCount });
  },
  markAllAsRead: () => {
    set({
      notifications: get().notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    });
  },
  removeNotification: (id) => {
    const notification = get().notifications.find((n) => n.id === id);
    const unreadCount = notification && !notification.read
      ? get().unreadCount - 1
      : get().unreadCount;
    set({
      notifications: get().notifications.filter((n) => n.id !== id),
      unreadCount,
    });
  },
  clearAll: () => set({ notifications: [], unreadCount: 0 }),
}));

// ============================================
// SCANS STORE
// ============================================

type ScanState = {
  scans: Scan[];
  activeScan: Scan | null;
  addScan: (scan: Omit<Scan, 'id'>) => string;
  updateScan: (id: string, updates: Partial<Scan>) => void;
  setActiveScan: (scan: Scan | null) => void;
  removeScan: (id: string) => void;
  clearScans: () => void;
};

export const useScanStore = create<ScanState>()(
  persist(
    (set, get) => ({
      scans: [],
      activeScan: null,
      addScan: (scan) => {
        const id = Math.random().toString(36).substring(2, 15);
        set({ scans: [{ ...scan, id }, ...get().scans] });
        return id;
      },
      updateScan: (id, updates) => {
        set({
          scans: get().scans.map((s) => (s.id === id ? { ...s, ...updates } : s)),
          activeScan:
            get().activeScan?.id === id
              ? { ...get().activeScan, ...updates }
              : get().activeScan,
        });
      },
      setActiveScan: (scan) => set({ activeScan: scan }),
      removeScan: (id) => {
        set({
          scans: get().scans.filter((s) => s.id !== id),
          activeScan: get().activeScan?.id === id ? null : get().activeScan,
        });
      },
      clearScans: () => set({ scans: [], activeScan: null }),
    }),
    {
      name: 'osint-fusion-scans',
      partialize: (state) => ({ scans: state.scans.slice(0, 50) }),
    }
  )
);

// ============================================
// UI STATE STORE
// ============================================

type UIState = {
  isLoading: boolean;
  loadingMessage: string;
  aiPanelOpen: boolean;
  graphFullscreen: boolean;
  settingsOpen: boolean;
  warningToast: { show: boolean; message: string } | null;
  activeAbortController: AbortController | null;
  setLoading: (loading: boolean, message?: string) => void;
  setAIPanelOpen: (open: boolean) => void;
  setGraphFullscreen: (fullscreen: boolean) => void;
  setSettingsOpen: (open: boolean) => void;
  showWarningToast: (message: string) => void;
  hideWarningToast: () => void;
  setActiveAbortController: (controller: AbortController | null) => void;
};

export const useUIStore = create<UIState>((set) => ({
  isLoading: false,
  loadingMessage: '',
  aiPanelOpen: false,
  graphFullscreen: false,
  settingsOpen: false,
  warningToast: null,
  activeAbortController: null,
  setLoading: (loading, message = '') => set({ isLoading: loading, loadingMessage: message }),
  setAIPanelOpen: (open) => set({ aiPanelOpen: open }),
  setGraphFullscreen: (fullscreen) => set({ graphFullscreen: fullscreen }),
  setSettingsOpen: (open) => set({ settingsOpen: open }),
  showWarningToast: (message) => set({ warningToast: { show: true, message } }),
  hideWarningToast: () => set({ warningToast: null }),
  setActiveAbortController: (controller) => set({ activeAbortController: controller }),
}));

// ============================================
// SEARCH HISTORY STORE
// ============================================

type SearchHistoryItem = {
  query: string;
  type: string;
  timestamp: string;
};

type SearchHistoryState = {
  history: SearchHistoryItem[];
  addSearch: (query: string, type: string) => void;
  clearHistory: () => void;
};

export const useSearchHistoryStore = create<SearchHistoryState>()(
  persist(
    (set, get) => ({
      history: [],
      addSearch: (query, type) => {
        set({
          history: [
            { query, type, timestamp: new Date().toISOString() },
            ...get().history.filter((h) => h.query !== query),
          ].slice(0, 100),
        });
      },
      clearHistory: () => set({ history: [] }),
    }),
    {
      name: 'osint-fusion-search-history',
    }
  )
);
