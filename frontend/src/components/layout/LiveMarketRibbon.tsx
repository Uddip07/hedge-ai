import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Skeleton } from '../common/Skeleton';
import { TrendingUp, TrendingDown, RefreshCw, AlertCircle } from 'lucide-react';

export const LiveMarketRibbon: React.FC = () => {
  const { tickerList, status, errorMessage, reconnect, isLoading } = useWebSocket();

  if (isLoading) {
    return (
      <div className="w-full bg-[#0D121F] border-b border-[#1E293B] px-4 py-2 flex items-center gap-4 overflow-hidden select-none">
        <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase shrink-0 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
          Market Stream
        </span>
        <div className="flex items-center gap-6 overflow-hidden flex-1">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="flex items-center gap-2 shrink-0">
              <Skeleton width={70} height={14} />
              <Skeleton width={50} height={14} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (status === 'ERROR' && tickerList.length === 0) {
    return (
      <div className="w-full bg-red-950/40 border-b border-red-900/40 px-4 py-1.5 flex items-center justify-between text-xs text-red-300">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400" />
          <span>Market Feed Disconnected: {errorMessage || 'WebSocket connection unreachable.'}</span>
        </div>
        <button
          onClick={reconnect}
          className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold bg-red-900/60 hover:bg-red-800 border border-red-700/60 rounded text-red-100 transition-colors"
        >
          <RefreshCw className="w-3 h-3" />
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="w-full bg-[#0D121F] border-b border-[#1E293B] px-4 py-1.5 flex items-center gap-4 overflow-hidden select-none">
      <div className="flex items-center gap-2 shrink-0">
        <span
          className={`w-2 h-2 rounded-full ${
            status === 'CONNECTED' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
          }`}
        />
        <span className="text-[10px] font-bold tracking-widest text-slate-400 uppercase">
          LIVE NSE/BSE
        </span>
      </div>

      <div className="flex items-center gap-6 overflow-x-auto no-scrollbar scroll-smooth flex-1 min-w-0 py-0.5">
        {tickerList.map((item) => {
          const isUp = item.change >= 0;
          const flashBg =
            item.direction === 'up'
              ? 'bg-emerald-950/60 text-emerald-300 ring-1 ring-emerald-500/40'
              : item.direction === 'down'
              ? 'bg-red-950/60 text-red-300 ring-1 ring-red-500/40'
              : 'hover:bg-slate-800/40';

          return (
            <div
              key={item.ticker}
              className={`flex items-center gap-2 px-2 py-0.5 rounded transition-all duration-300 shrink-0 cursor-pointer ${flashBg}`}
            >
              <span className="text-xs font-bold text-slate-200 tracking-tight">
                {item.name || item.ticker.split('.')[0]}
              </span>
              <span className="text-xs font-mono font-semibold text-slate-100">
                ₹{item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
              <div
                className={`flex items-center gap-0.5 text-[11px] font-mono font-medium ${
                  isUp ? 'text-emerald-400' : 'text-red-400'
                }`}
              >
                {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                <span>
                  {isUp ? '+' : ''}
                  {item.change.toFixed(2)} ({isUp ? '+' : ''}
                  {item.change_percent.toFixed(2)}%)
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {status === 'RECONNECTING' && (
        <span className="text-[10px] font-mono text-amber-400 shrink-0 flex items-center gap-1">
          <RefreshCw className="w-3 h-3 animate-spin" />
          Reconnecting...
        </span>
      )}
    </div>
  );
};
