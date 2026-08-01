import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorAlertProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title = 'Backend Request Error',
  message,
  onRetry,
}) => {
  return (
    <div className="flex items-start justify-between rounded-lg border border-rose-900/60 bg-rose-950/40 p-4 text-rose-200">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 text-rose-400 shrink-0" />
        <div>
          <h4 className="text-sm font-semibold text-rose-300">{title}</h4>
          <p className="mt-1 text-xs text-rose-200/90 font-mono">{message}</p>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1.5 rounded border border-rose-800 bg-rose-900/40 px-3 py-1.5 text-xs font-medium text-rose-100 hover:bg-rose-900/80 transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Retry
        </button>
      )}
    </div>
  );
};
