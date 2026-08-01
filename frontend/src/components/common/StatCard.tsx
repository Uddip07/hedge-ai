import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: LucideIcon;
  format?: 'currency' | 'percent' | 'number' | 'raw';
  subtext?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeLabel = 'vs prev day',
  icon: Icon,
  subtext,
}) => {
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className="glass-panel glass-panel-hover rounded-xl p-4 relative overflow-hidden group">
      {/* Background Subtle Gradient Glow */}
      <div
        className={`absolute -right-8 -bottom-8 w-28 h-28 rounded-full blur-2xl transition-opacity duration-300 ${
          isPositive ? 'bg-emerald-500/10' : change !== undefined ? 'bg-rose-500/10' : 'bg-cyan-500/10'
        }`}
      />

      <div className="flex items-center justify-between relative z-10">
        <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className="p-2 rounded-lg bg-white/5 text-slate-300 border border-white/5 group-hover:border-cyan-500/30 transition-colors">
            <Icon className="h-4 w-4 text-cyan-400" />
          </div>
        )}
      </div>

      <div className="mt-2 relative z-10">
        <div className="text-2xl font-mono font-bold text-slate-100 num-tabular tracking-tight">
          {value}
        </div>

        {(change !== undefined || subtext) && (
          <div className="mt-2 flex items-center justify-between text-xs font-mono">
            {change !== undefined && (
              <div
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                  isPositive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                }`}
              >
                {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                <span>
                  {isPositive ? '+' : ''}
                  {change.toFixed(2)}%
                </span>
              </div>
            )}

            {subtext ? (
              <span className="text-slate-500 text-[11px]">{subtext}</span>
            ) : (
              changeLabel && <span className="text-slate-500 text-[11px]">{changeLabel}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
