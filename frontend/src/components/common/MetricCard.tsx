import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export interface MetricCardProps {
  title: string;
  value?: string | number;
  changePercent?: number;
  subtitle?: string;
  status?: string;
  latencyMs?: number;
  provider?: string;
  lastUpdated?: string;
  error?: string;
  icon?: React.ReactNode;
  trendData?: number[];
  tooltip?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
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
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ duration: 0.15 }}
      className="rounded-xl border border-slate-800/80 bg-slate-900/80 p-5 shadow-lg backdrop-blur-md transition-all hover:border-slate-700/80 hover:shadow-cyan-950/20"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          {icon && <div className="rounded-lg bg-slate-800/80 p-2 text-cyan-400 border border-slate-700/60">{icon}</div>}
          <div>
            <h3 className="text-xs font-medium uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              {title}
              {tooltip && (
                <span title={tooltip} className="cursor-help text-slate-500 hover:text-slate-300">
                  <Info className="h-3 w-3" />
                </span>
              )}
            </h3>
            {subtitle && <p className="text-[10px] text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
        </div>

        {status && <StatusBadge status={status} size="sm" />}

        {changePercent !== undefined && (
          <div
            className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium num-tabular ${
              isPositive
                ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                : 'bg-rose-950/80 text-rose-400 border border-rose-800/60'
            }`}
          >
            {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            <span>{isPositive ? '+' : ''}{changePercent.toFixed(2)}%</span>
          </div>
        )}
      </div>

      {value !== undefined && (
        <div className="mt-4">
          <div className="text-2xl font-bold tracking-tight text-slate-100 font-mono num-tabular">
            {value}
          </div>
        </div>
      )}

      {(latencyMs !== undefined || provider || lastUpdated) && (
        <div className="mt-4 pt-3 border-t border-slate-800/60 grid grid-cols-2 gap-2 text-[11px] text-slate-400 font-mono">
          {latencyMs !== undefined && (
            <div>
              <span className="text-slate-500">Latency:</span>{' '}
              <span className="text-slate-200">{latencyMs} ms</span>
            </div>
          )}
          {provider && (
            <div className="text-right truncate">
              <span className="text-slate-500">Provider:</span>{' '}
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
        <div className="mt-3 rounded-lg border border-rose-900/50 bg-rose-950/40 p-2.5 text-xs text-rose-300">
          <span className="font-semibold">Error:</span> {error}
        </div>
      )}
    </motion.div>
  );
};
