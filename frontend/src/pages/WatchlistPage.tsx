import React, { useState } from 'react';
import { Bookmark, Plus, Bell, Trash2, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

export const WatchlistPage: React.FC = () => {
  const { tickerList } = useWebSocket();

  const initialItems = [
    { symbol: 'RELIANCE', name: 'Reliance Industries', price: 2980.45, change: 1.09, alertHigh: 3100, alertLow: 2850 },
    { symbol: 'TRENT', name: 'Trent Limited', price: 6420.0, change: 4.8, alertHigh: 6700, alertLow: 6100 },
    { symbol: 'DELHIVERY', name: 'Delhivery Ltd', price: 412.3, change: -1.2, alertHigh: 450, alertLow: 390 },
    { symbol: 'INFY', name: 'Infosys Limited', price: 1820.6, change: 0.8, alertHigh: 1950, alertLow: 1750 },
  ];

  const [watchlist, setWatchlist] = useState(initialItems);
  const [newSymbol, setNewSymbol] = useState('');

  const handleAddSymbol = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim()) return;
    const sym = newSymbol.trim().toUpperCase();
    if (watchlist.some((w) => w.symbol === sym)) return;

    setWatchlist((prev) => [
      ...prev,
      {
        symbol: sym,
        name: `${sym} Limited`,
        price: 1500.0,
        change: 0.5,
        alertHigh: 1650,
        alertLow: 1350,
      },
    ]);
    setNewSymbol('');
  };

  const handleRemove = (sym: string) => {
    setWatchlist((prev) => prev.filter((item) => item.symbol !== sym));
  };

  return (
    <div className="space-y-6 w-full max-w-full min-w-0 font-mono">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#121826] p-5 rounded-2xl border border-[#1E293B]">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <Bookmark className="h-4 w-4" />
            <span>REALTIME PRICE ALERTS & WATCHLIST</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Watchlist & Signal Triggers</h1>
          <p className="text-xs text-slate-400">
            Custom ticker monitoring, price threshold alerts, and instant execution shortcuts.
          </p>
        </div>

        <form onSubmit={handleAddSymbol} className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Add ticker (e.g. TATAMOTORS)..."
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            className="bg-slate-900 border border-[#1E293B] rounded-xl px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-56 md:w-64"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-950/50"
          >
            <Plus className="h-4 w-4" />
            <span>Add</span>
          </button>
        </form>
      </div>

      {/* Watchlist Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {watchlist.map((item) => {
          const live = tickerList.find((t) => t.ticker.startsWith(item.symbol));
          const currentPrice = live ? live.price : item.price;
          const currentChange = live ? live.change_percent : item.change;
          const isBull = currentChange >= 0;

          return (
            <div
              key={item.symbol}
              className="bg-[#121826] hover:bg-slate-800/40 rounded-2xl p-5 border border-[#1E293B] space-y-3 relative group transition-colors min-w-0"
            >
              <div className="flex items-center justify-between">
                <div className="truncate pr-2">
                  <div className="font-bold text-base text-slate-100">{item.symbol}</div>
                  <div className="text-[11px] text-slate-400 truncate">{item.name}</div>
                </div>
                <button
                  onClick={() => handleRemove(item.symbol)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-800 transition-colors shrink-0"
                  title="Remove from watchlist"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="flex items-baseline justify-between pt-2 border-t border-[#1E293B]">
                <div className="text-xl font-bold text-slate-100 num-tabular">
                  ₹{currentPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <div
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1 ${
                    isBull
                      ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40'
                      : 'bg-red-950/60 text-red-400 border border-red-800/40'
                  }`}
                >
                  {isBull ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                  {isBull ? '+' : ''}
                  {currentChange.toFixed(2)}%
                </div>
              </div>

              {/* Price Alerts */}
              <div className="pt-2 border-t border-[#1E293B] flex items-center justify-between text-[10px] text-slate-400">
                <div className="flex items-center gap-1">
                  <Bell className="h-3 w-3 text-amber-400" />
                  <span>High: ₹{item.alertHigh}</span>
                </div>
                <div>Low: ₹{item.alertLow}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
