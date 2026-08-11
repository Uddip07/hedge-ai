import React, { useState, useEffect } from 'react';
import { WifiOff, RefreshCw } from 'lucide-react';

export const OfflineBanner = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="w-full bg-rose-950 border-b border-rose-800 px-4 py-2 text-xs font-mono text-rose-200 flex items-center justify-between z-50">
      <div className="flex items-center gap-2">
        <WifiOff className="h-4 w-4 text-rose-400" />
        <span className="font-bold">Network Offline:</span>
        <span>Local machine has lost internet connectivity. Reconnecting...</span>
      </div>
      <button
        onClick={() => window.location.reload()}
        className="flex items-center gap-1 px-2.5 py-1 rounded bg-rose-900 hover:bg-rose-800 text-[11px] font-semibold border border-rose-700 transition-colors"
      >
        <RefreshCw className="h-3 w-3" />
        Reload
      </button>
    </div>
  );
};
