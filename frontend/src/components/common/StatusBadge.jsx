import React from 'react';

export const StatusBadge = ({ status, size = 'md', className = '' }) => {
  const clean = String(status || 'UNKNOWN').toUpperCase();

  const isHealthy = ['HEALTHY', 'ONLINE', 'CONNECTED', 'READY', 'ALIVE', 'COMPLETED', 'APPROVED', 'ACTIVE', 'BUY', 'STRONG_BUY', '200', '201'].includes(clean);
  const isWarning = ['DEGRADED', 'RECONNECTING', 'PENDING', 'RUNNING', 'PARTIAL', 'HOLD', 'NEUTRAL', '300', '307'].includes(clean);
  const isDanger = ['UNHEALTHY', 'ERROR', 'FAILED', 'DISCONNECTED', 'REJECTED', 'SELL', 'STRONG_SELL', 'ERR', '400', '404', '422', '500'].includes(clean);

  const sizeStyles = {
    xs: 'px-1.5 py-0.5 text-[9px]',
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-xs',
  };

  let colorStyle = 'bg-slate-800 text-slate-300 border-slate-700';
  if (isHealthy) {
    colorStyle = 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80';
  } else if (isWarning) {
    colorStyle = 'bg-amber-950/80 text-amber-300 border-amber-800/80';
  } else if (isDanger) {
    colorStyle = 'bg-rose-950/80 text-rose-300 border-rose-800/80';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md font-mono font-bold uppercase tracking-wider border select-none ${sizeStyles[size] || sizeStyles.md} ${colorStyle} ${className}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isHealthy
            ? 'bg-emerald-400'
            : isWarning
            ? 'bg-amber-400 animate-pulse'
            : isDanger
            ? 'bg-rose-400'
            : 'bg-slate-400'
        }`}
      />
      <span>{clean}</span>
    </span>
  );
};
