import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const StatCard = ({
  title,
  value,
  change,
  changeLabel = 'vs prev day',
  icon: Icon,
  subtext,
  className = '',
}) => {
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className={`rounded-xl border border-[#162235] bg-[#0d1524] p-4 relative overflow-hidden group hover:border-[#1f3350] transition-colors ${className}`}>
      <div className="flex items-center justify-between relative z-10">
        <span className="text-[11px] font-mono font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className="p-1.5 rounded-lg bg-slate-800/60 text-cyan-400 border border-[#162235] group-hover:border-cyan-500/30 transition-colors">
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      <div className="mt-2 relative z-10">
        <div className="text-xl font-mono font-bold text-slate-100 num-tabular tracking-tight">
          {value !== undefined && value !== null && value !== '' ? value : '—'}
        </div>

        {(change !== undefined || subtext) && (
          <div className="mt-2 flex items-center justify-between text-xs font-mono">
            {change !== undefined && (
              <div
                className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-semibold num-tabular ${
                  isPositive
                    ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                    : 'bg-rose-950/80 text-rose-400 border border-rose-800/60'
                }`}
              >
                {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                <span>
                  {isPositive ? '+' : ''}
                  {typeof change === 'number' ? change.toFixed(2) : change}%
                </span>
              </div>
            )}

            {subtext ? (
              <span className="text-slate-500 text-[11px] truncate">{subtext}</span>
            ) : (
              changeLabel && <span className="text-slate-500 text-[11px] truncate">{changeLabel}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
