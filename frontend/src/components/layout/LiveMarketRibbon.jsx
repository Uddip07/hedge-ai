import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Skeleton } from '../common/Skeleton';
import { TrendingUp, TrendingDown, RefreshCw, AlertCircle } from 'lucide-react';

export const LiveMarketRibbon = () => {
  const { tickerList, status, errorMessage, reconnect, isLoading } = useWebSocket();

  if (isLoading) {
    return (
      <div className="w-full bg-[#090e17] border-b border-[#162235] px-4 py-2 flex items-center gap-4 overflow-hidden select-none font-mono">
        <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase shrink-0 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-500 animate-ping" />
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
      <div className="w-full bg-rose-950/40 border-b border-rose-900/40 px-4 py-1.5 flex items-center justify-between text-xs text-rose-300 font-mono">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <span>Market Stream: {errorMessage || 'WebSocket connecting to localhost:8000...'}</span>
        </div>
        <button
          type="button"
          onClick={reconnect}
          className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold bg-rose-900/60 hover:bg-rose-800 border border-rose-700/60 rounded text-rose-100 transition-colors cursor-pointer"
        >
          <RefreshCw className="w-3 h-3" />
          Retry Stream
        </button>
      </div>
    );
  }

  const firstItem = tickerList[0];
  const isMarketOpen = firstItem?.is_market_open ?? (firstItem?.market_state === 'OPEN');
  const marketBadgeText = isMarketOpen ? 'NSE/BSE (DELAYED)' : 'NSE/BSE (LAST CLOSE)';

  return (
    <div className="w-full bg-[#090e17] border-b border-[#162235] px-4 py-1.5 flex items-center gap-4 overflow-hidden select-none font-mono text-xs">
      <div className="flex items-center gap-2 shrink-0">
        <span
          className={`w-2 h-2 rounded-full ${
            status === 'CONNECTED'
              ? isMarketOpen
                ? 'bg-emerald-400 animate-pulse'
                : 'bg-slate-400'
              : 'bg-amber-400'
          }`}
        />
        <span className="text-[10px] font-bold tracking-widest text-slate-400 uppercase">
          {marketBadgeText}
        </span>
      </div>

      <div className="flex items-center gap-6 overflow-x-auto scrollbar-none flex-1 min-w-0 py-0.5">
        {tickerList.map((item) => {
          const isUp = item.change >= 0;
          const flashBg =
            item.direction === 'up'
              ? 'bg-emerald-950/60 text-emerald-300 ring-1 ring-emerald-500/40'
              : item.direction === 'down'
              ? 'bg-rose-950/60 text-rose-300 ring-1 ring-rose-500/40'
              : 'hover:bg-slate-800/40';

          const priceFormatted =
            typeof item.price === 'number' && item.price > 0
              ? `₹${item.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
              : '—';

          const changePctFormatted =
            typeof item.change_percent === 'number'
              ? `${isUp ? '+' : ''}${item.change_percent.toFixed(2)}%`
              : '—';

          return (
            <div
              key={item.ticker}
              className={`flex items-center gap-2 px-2 py-0.5 rounded transition-all duration-300 shrink-0 select-none ${flashBg}`}
            >
              <span className="text-xs font-bold text-slate-200 tracking-tight">
                {item.name || item.ticker.split('.')[0]}
              </span>
              <span className="text-xs font-mono font-semibold text-slate-100 num-tabular">
                {priceFormatted}
              </span>
              <div
                className={`flex items-center gap-0.5 text-[11px] font-mono font-medium num-tabular ${
                  isUp ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                <span>{changePctFormatted}</span>
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
