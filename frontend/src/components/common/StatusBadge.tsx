import React from 'react';

export interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'dot' | 'solid' | 'outline';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  variant = 'dot',
}) => {
  const s = status.toUpperCase().trim();

  let bgClass = 'bg-slate-800/90 text-slate-300 border-slate-700/80';
  let dotClass = 'bg-slate-400';

  if (
    s === 'HEALTHY' ||
    s === 'RUNNING' ||
    s === 'ONLINE' ||
    s === '200' ||
    s === 'OK' ||
    s === 'BUY' ||
    s === 'STRONG_BUY' ||
    s === 'LOW' ||
    s === 'SUCCESS' ||
    s === 'OPEN' ||
    s === 'ACTIVE'
  ) {
    bgClass = 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60 shadow-sm shadow-emerald-950/40';
    dotClass = 'bg-emerald-400 animate-pulse';
  } else if (
    s === 'DEGRADED' ||
    s === 'WARNING' ||
    s === 'HOLD' ||
    s === 'PENDING' ||
    s === 'MEDIUM' ||
    s === 'MODERATE' ||
    s === 'NEUTRAL'
  ) {
    bgClass = 'bg-amber-950/80 text-amber-300 border-amber-800/60 shadow-sm shadow-amber-950/40';
    dotClass = 'bg-amber-400';
  } else if (
    s === 'FAILED' ||
    s === 'ERROR' ||
    s === 'OFFLINE' ||
    s === '500' ||
    s === 'ERR' ||
    s === 'SELL' ||
    s === 'STRONG_SELL' ||
    s === 'HIGH' ||
    s === 'UNREACHABLE' ||
    s === 'CRITICAL'
  ) {
    bgClass = 'bg-rose-950/80 text-rose-300 border-rose-800/60 shadow-sm shadow-rose-950/40';
    dotClass = 'bg-rose-400';
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-[11px]',
    md: 'px-2.5 py-1 text-xs font-medium',
    lg: 'px-3 py-1.5 text-sm font-semibold',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border font-mono tracking-tight uppercase ${bgClass} ${sizes[size]}`}>
      {variant === 'dot' && <span className={`h-1.5 w-1.5 rounded-full shrink-0 ${dotClass}`} />}
      <span>{status.replace(/_/g, ' ')}</span>
    </span>
  );
};
