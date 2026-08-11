import { useState, useEffect } from 'react';

let toastListeners = [];
let toastQueue = [];

export const toast = {
  success: (title, message) => showToast({ type: 'success', title, message }),
  error: (title, message) => showToast({ type: 'error', title, message }),
  warning: (title, message) => showToast({ type: 'warning', title, message }),
  info: (title, message) => showToast({ type: 'info', title, message }),
};

function showToast(toastItem) {
  const id = Math.random().toString(36).substring(2, 9);
  const newToast = { ...toastItem, id };
  toastQueue = [...toastQueue, newToast];
  toastListeners.forEach((fn) => fn(toastQueue));

  setTimeout(() => {
    toastQueue = toastQueue.filter((t) => t.id !== id);
    toastListeners.forEach((fn) => fn(toastQueue));
  }, 4500);
}

export function useToast() {
  const [toasts, setToasts] = useState(toastQueue);

  useEffect(() => {
    toastListeners.push(setToasts);
    return () => {
      toastListeners = toastListeners.filter((fn) => fn !== setToasts);
    };
  }, []);

  const removeToast = (id) => {
    toastQueue = toastQueue.filter((t) => t.id !== id);
    toastListeners.forEach((fn) => fn(toastQueue));
  };

  return { toasts, removeToast, toast };
}
