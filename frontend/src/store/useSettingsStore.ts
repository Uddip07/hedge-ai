import { create } from 'zustand';
import { ApiCallLog } from '../types/api';

interface SettingsState {
  backendUrl: string;
  autoRefreshInterval: number; // in milliseconds
  developerMode: boolean;
  theme: 'dark' | 'light';
  apiLogs: ApiCallLog[];
  setBackendUrl: (url: string) => void;
  setAutoRefreshInterval: (interval: number) => void;
  setDeveloperMode: (enabled: boolean) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  addApiLog: (log: Omit<ApiCallLog, 'id'>) => void;
  clearLogs: () => void;
}

const defaultBackendUrl = import.meta.env.VITE_API_BASE_URL || '/api';

export const useSettingsStore = create<SettingsState>((set) => ({
  backendUrl: defaultBackendUrl,
  autoRefreshInterval: 5000,
  developerMode: true,
  theme: 'dark',
  apiLogs: [],
  setBackendUrl: (url) => set({ backendUrl: url }),
  setAutoRefreshInterval: (interval) => set({ autoRefreshInterval: interval }),
  setDeveloperMode: (enabled) => set({ developerMode: enabled }),
  setTheme: (theme) => set({ theme }),
  addApiLog: (log) =>
    set((state) => ({
      apiLogs: [
        {
          ...log,
          id: Math.random().toString(36).substring(2, 9),
        },
        ...state.apiLogs.slice(0, 99), // Keep latest 100 logs
      ],
    })),
  clearLogs: () => set({ apiLogs: [] }),
}));
