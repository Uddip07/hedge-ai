import React, { useState, useEffect } from 'react';
import { WifiOff, RefreshCw } from 'lucide-react';

export const OfflineBanner: React.FC = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline) return null;

  return (
    <div className="bg-amber-950/90 border-b border-amber-800/60 px-4 py-2 text-amber-200 text-xs flex items-center justify-between z-50">
      <div className="flex items-center gap-2">
        <WifiOff className="w-4 h-4 text-amber-400" />
        <span className="font-semibold">Network Connection Disconnected:</span>
        <span className="hidden md:inline text-amber-300">
          Real-time market feeds & data execution paused until connection is restored.
        </span>
      </div>
      <button
        onClick={() => window.location.reload()}
        className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-amber-900/60 hover:bg-amber-800 border border-amber-700/60 rounded text-amber-100 transition-colors"
      >
        <RefreshCw className="w-3 h-3" />
        Reconnect
      </button>
    </div>
  );
};
