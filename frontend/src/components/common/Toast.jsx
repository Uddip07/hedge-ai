import React from 'react';
import { useToast } from '../../hooks/useToast';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export const Toast = () => {
  const { toasts, removeToast } = useToast();

  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none font-mono">
      {toasts.map((t) => {
        const isSuccess = t.type === 'success';
        const isError = t.type === 'error';
        const isWarning = t.type === 'warning';

        return (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-start justify-between gap-3 p-3.5 rounded-xl border shadow-2xl backdrop-blur-md transition-all ${
              isSuccess
                ? 'bg-emerald-950/90 border-emerald-800/80 text-emerald-100'
                : isError
                ? 'bg-rose-950/90 border-rose-800/80 text-rose-100'
                : isWarning
                ? 'bg-amber-950/90 border-amber-800/80 text-amber-100'
                : 'bg-slate-900/90 border-slate-700/80 text-slate-100'
            }`}
          >
            <div className="flex items-start gap-2.5">
              {isSuccess && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />}
              {isError && <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />}
              {isWarning && <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />}
              {!isSuccess && !isError && !isWarning && <Info className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />}
              <div className="space-y-0.5 text-xs">
                {t.title && <div className="font-bold">{t.title}</div>}
                {t.message && <div className="text-[11px] opacity-90 leading-relaxed">{t.message}</div>}
              </div>
            </div>

            <button
              onClick={() => removeToast(t.id)}
              className="p-1 rounded text-slate-400 hover:text-white transition-colors shrink-0"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
