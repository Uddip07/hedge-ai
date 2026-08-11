import React from 'react';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export const MetricCard = ({
  title,
  value,
  changePercent,
  subtitle,
  status,
  latencyMs,
  provider = 'Yahoo Finance / Backend',
  lastUpdated,
  error,
  icon,
  tooltip,
}) => {
  const isPositive = changePercent !== undefined && changePercent >= 0;

  return (
    <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 shadow-lg transition-all hover:border-[#1f3350]">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          {icon && (
            <div className="rounded-lg bg-slate-800/80 p-2 text-cyan-400 border border-slate-700/60">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-xs font-medium uppercase tracking-wider text-slate-400 flex items-center gap-1.5 font-mono">
              {title}
              {tooltip && (
                <span title={tooltip} className="cursor-help text-slate-500 hover:text-slate-300">
                  <Info className="h-3 w-3" />
                </span>
              )}
            </h3>
            {subtitle && <p className="text-[10px] text-slate-500 mt-0.5 font-mono">{subtitle}</p>}
          </div>
        </div>

        {status && <StatusBadge status={status} size="sm" />}

        {changePercent !== undefined && (
          <div
            className={`flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium font-mono num-tabular ${
              isPositive
                ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                : 'bg-rose-950/80 text-rose-400 border border-rose-800/60'
            }`}
          >
            {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            <span>
              {isPositive ? '+' : ''}
              {typeof changePercent === 'number' ? changePercent.toFixed(2) : changePercent}%
            </span>
          </div>
        )}
      </div>

      <div className="mt-4">
        <div className="text-2xl font-bold tracking-tight text-slate-100 font-mono num-tabular">
          {value !== undefined && value !== null && value !== '' ? value : '—'}
        </div>
      </div>

      {(latencyMs !== undefined || provider || lastUpdated) && (
        <div className="mt-4 pt-3 border-t border-[#162235] grid grid-cols-2 gap-2 text-[11px] text-slate-400 font-mono">
          {latencyMs !== undefined && (
            <div>
              <span className="text-slate-500">Latency:</span>{' '}
              <span className="text-slate-200">{latencyMs} ms</span>
            </div>
          )}
          {provider && (
            <div className="text-right truncate">
              <span className="text-slate-500">Source:</span>{' '}
              <span className="text-slate-200" title={provider}>{provider}</span>
            </div>
          )}
          {lastUpdated && (
            <div className="col-span-2 text-slate-500 text-[10px]">
              Updated: <span className="text-slate-400">{lastUpdated}</span>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mt-3 rounded-lg border border-rose-900/50 bg-rose-950/40 p-2.5 text-xs text-rose-300 font-mono">
          <span className="font-semibold">Error:</span> {error}
        </div>
      )}
    </div>
  );
};
