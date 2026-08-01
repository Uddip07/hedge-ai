import React from 'react';
import { useToast, ToastItem } from '../../hooks/useToast';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((item: ToastItem) => {
        let borderClass = 'border-blue-500/40 bg-[#121826]/95 text-blue-300';
        let Icon = Info;

        if (item.type === 'success') {
          borderClass = 'border-emerald-500/40 bg-[#121826]/95 text-emerald-300';
          Icon = CheckCircle2;
        } else if (item.type === 'error') {
          borderClass = 'border-red-500/40 bg-[#121826]/95 text-red-300';
          Icon = AlertCircle;
        } else if (item.type === 'warning') {
          borderClass = 'border-amber-500/40 bg-[#121826]/95 text-amber-300';
          Icon = AlertTriangle;
        }

        return (
          <div
            key={item.id}
            className={`pointer-events-auto flex items-start gap-3 p-3 rounded-lg border shadow-xl backdrop-blur transition-all duration-200 ${borderClass}`}
          >
            <Icon className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <h4 className="text-xs font-semibold text-slate-100">{item.title}</h4>
              {item.message && <p className="text-[11px] text-slate-300 mt-0.5 leading-tight">{item.message}</p>}
            </div>
            <button
              onClick={() => dismiss(item.id)}
              className="text-slate-400 hover:text-slate-100 p-0.5 rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
