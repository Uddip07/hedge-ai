import React, { useState } from 'react';
import { Bookmark, Plus, Bell, Trash2, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

export const WatchlistPage: React.FC = () => {
  const [watchlist, setWatchlist] = useState([
    { symbol: 'RELIANCE', name: 'Reliance Industries', price: '₹2,638.50', change: +2.15, alertHigh: 2700, alertLow: 2550 },
    { symbol: 'TRENT', name: 'Trent Limited', price: '₹6,420.00', change: +4.80, alertHigh: 6500, alertLow: 6000 },
    { symbol: 'DELHIVERY', name: 'Delhivery Ltd', price: '₹412.30', change: -1.20, alertHigh: 450, alertLow: 390 },
    { symbol: 'INFY', name: 'Infosys Limited', price: '₹1,820.75', change: +0.45, alertHigh: 1900, alertLow: 1750 },
  ]);

  const [newSymbol, setNewSymbol] = useState('');

  const handleAddSymbol = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim()) return;
    setWatchlist((prev) => [
      ...prev,
      {
        symbol: newSymbol.trim().toUpperCase(),
        name: `${newSymbol.trim().toUpperCase()} Limited`,
        price: '₹1,250.00',
        change: +1.0,
        alertHigh: 1400,
        alertLow: 1100,
      },
    ]);
    setNewSymbol('');
  };

  const handleRemove = (sym: string) => {
    setWatchlist((prev) => prev.filter((item) => item.symbol !== sym));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono"
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <Bookmark className="h-4 w-4" />
            <span>REALTIME PRICE ALERTS & WATCHLIST</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Watchlist & Signal Triggers</h1>
          <p className="text-xs text-slate-400">Custom ticker monitoring, price threshold alerts, and instant execution shortcuts.</p>
        </div>

        <form onSubmit={handleAddSymbol} className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Add ticker (e.g. TATAMOTORS)..."
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-64"
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {watchlist.map((item) => {
          const isBull = item.change >= 0;
          return (
            <div key={item.symbol} className="glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 space-y-3 relative group">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-base text-slate-100">{item.symbol}</div>
                  <div className="text-[11px] text-slate-400">{item.name}</div>
                </div>
                <button
                  onClick={() => handleRemove(item.symbol)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-white/5 transition-colors"
                  title="Remove from watchlist"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="flex items-baseline justify-between pt-2 border-t border-white/5">
                <div className="text-xl font-bold text-slate-100 num-tabular">{item.price}</div>
                <div className={`text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1 ${isBull ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}`}>
                  {isBull ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                  {isBull ? '+' : ''}{item.change.toFixed(2)}%
                </div>
              </div>

              {/* Price Alerts */}
              <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] text-slate-400">
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
    </motion.div>
  );
};
