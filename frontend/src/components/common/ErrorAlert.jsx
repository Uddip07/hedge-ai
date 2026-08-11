import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export const ErrorAlert = ({
  title = 'Service Query Failed',
  message = 'An error occurred while communicating with the backend API.',
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`rounded-xl border border-rose-800/60 bg-rose-950/30 p-4 font-mono text-xs text-rose-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${className}`}
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <div className="font-bold text-rose-200">{title}</div>
          <div className="text-[11px] text-rose-300/90 leading-relaxed">{message}</div>
        </div>
      </div>

      {onRetry && (
        <Button
          variant="destructive"
          size="xs"
          onClick={onRetry}
          leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          className="shrink-0 font-bold"
        >
          Retry
        </Button>
      )}
    </div>
  );
};
