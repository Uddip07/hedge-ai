import { useState, useCallback } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  durationMs?: number;
}

let toastListeners: Array<(toasts: ToastItem[]) => void> = [];
let toastState: ToastItem[] = [];

function notify(): void {
  toastListeners.forEach((listener) => listener([...toastState]));
}

export const toast = {
  show(type: ToastType, title: string, message?: string, durationMs = 4000): void {
    const id = Math.random().toString(36).substring(2, 9);
    const item: ToastItem = { id, type, title, message, durationMs };
    toastState = [...toastState, item];
    notify();

    if (durationMs > 0) {
      setTimeout(() => {
        toast.dismiss(id);
      }, durationMs);
    }
  },
  success(title: string, message?: string): void {
    toast.show('success', title, message);
  },
  error(title: string, message?: string): void {
    toast.show('error', title, message, 6000);
  },
  warning(title: string, message?: string): void {
    toast.show('warning', title, message);
  },
  info(title: string, message?: string): void {
    toast.show('info', title, message);
  },
  dismiss(id: string): void {
    toastState = toastState.filter((t) => t.id !== id);
    notify();
  },
};

export function useToast(): { toasts: ToastItem[]; dismiss: (id: string) => void } {
  const [toasts, setToasts] = useState<ToastItem[]>(toastState);

  const subscribe = useCallback(() => {
    const listener = (newToasts: ToastItem[]) => setToasts(newToasts);
    toastListeners.push(listener);
    return () => {
      toastListeners = toastListeners.filter((l) => l !== listener);
    };
  }, []);

  useState(() => {
    subscribe();
  });

  return { toasts, dismiss: toast.dismiss };
}
