import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ message = 'Loading financial telemetry...', height = 240 }) => {
  return (
    <div
      style={{ minHeight: height }}
      className="w-full flex flex-col items-center justify-center gap-3 p-8 font-mono text-xs text-slate-400"
    >
      <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
      <span className="tracking-wide">{message}</span>
    </div>
  );
};
