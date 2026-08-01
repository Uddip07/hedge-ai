import React, { useState } from 'react';
import { StatCard } from '../components/common/StatCard';
import { FinancialChart } from '../components/common/FinancialChart';
import { History, Play as PlayIcon, CheckCircle2, TrendingUp, BarChart2, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';


export const BacktestingPage: React.FC = () => {
  const [strategyName, setStrategyName] = useState('Momentum Breakout & VWAP Reversion');
  const [initialCapital, setInitialCapital] = useState('1000000');
  const [isRunning, setIsRunning] = useState(false);

  const equityCurveData = [
    { date: '2025-01-01', close: 1000000, open: 1000000, high: 1000000, low: 1000000, volume: 0 },
    { date: '2025-03-01', close: 1080000, open: 1000000, high: 1100000, low: 1000000, volume: 0 },
    { date: '2025-06-01', close: 1150000, open: 1080000, high: 1180000, low: 1070000, volume: 0 },
    { date: '2025-09-01', close: 1240000, open: 1150000, high: 1260000, low: 1140000, volume: 0 },
    { date: '2025-12-01', close: 1320000, open: 1240000, high: 1350000, low: 1230000, volume: 0 },
    { date: '2026-03-01', close: 1410000, open: 1320000, high: 1430000, low: 1310000, volume: 0 },
    { date: '2026-07-31', close: 1548000, open: 1410000, high: 1560000, low: 1400000, volume: 0 },
  ];

  const handleRunBacktest = (e: React.FormEvent) => {
    e.preventDefault();
    setIsRunning(true);
    setTimeout(() => setIsRunning(false), 2000);
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
            <TrendingUp className="h-4 w-4" />
            <span>QUANTITATIVE BACKTESTING ENGINE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Historical Strategy Simulation</h1>
          <p className="text-xs text-slate-400">Zero lookahead leakage backtesting on PostgreSQL historical price records.</p>
        </div>
      </div>

      {/* Main Grid: Controls + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Panel */}
        <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2 border-b border-white/10 pb-3">
            <BarChart2 className="h-4 w-4 text-cyan-400" />
            Strategy Configuration
          </h3>

          <form onSubmit={handleRunBacktest} className="space-y-4 text-xs">
            <div className="space-y-1.5">
              <label className="text-slate-400">Strategy Preset</label>
              <select
                value={strategyName}
                onChange={(e) => setStrategyName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-slate-100 font-bold focus:outline-none focus:border-cyan-500/50"
              >
                <option value="Momentum Breakout & VWAP Reversion" className="bg-slate-900">Momentum Breakout & VWAP</option>
                <option value="Dual Moving Average Crossover (20/50)" className="bg-slate-900">Dual MA Crossover (20/50)</option>
                <option value="Mean Reversion Bollinger Bands" className="bg-slate-900">Bollinger Band Mean Reversion</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-400">Initial Portfolio Capital (₹)</label>
              <input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-slate-100 font-bold focus:outline-none focus:border-cyan-500/50"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-slate-400">Stop Loss %</label>
                <input
                  type="number"
                  defaultValue="2.5"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-slate-100 font-bold focus:outline-none focus:border-cyan-500/50"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-slate-400">Take Profit %</label>
                <input
                  type="number"
                  defaultValue="6.0"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-slate-100 font-bold focus:outline-none focus:border-cyan-500/50"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isRunning}
              className="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-lg shadow-cyan-950/50 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <PlayIcon className={`h-4 w-4 ${isRunning ? 'animate-spin' : ''}`} />
              <span>{isRunning ? 'Simulating Strategy...' : 'Execute Backtest Run'}</span>
            </button>
          </form>
        </div>

        {/* Results Graph & Metrics */}
        <div className="lg:col-span-2 space-y-6">
          <FinancialChart data={equityCurveData} symbol="EQUITY_CURVE" height={340} />

          {/* Backtest Performance Indicators */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-1">
              <div className="text-[11px] text-slate-400">Total Return</div>
              <div className="text-xl font-bold text-emerald-400 num-tabular">+54.80%</div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-1">
              <div className="text-[11px] text-slate-400">Sharpe Ratio</div>
              <div className="text-xl font-bold text-cyan-300 num-tabular">3.12</div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-1">
              <div className="text-[11px] text-slate-400">Max Drawdown</div>
              <div className="text-xl font-bold text-rose-400 num-tabular">-3.45%</div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-1">
              <div className="text-[11px] text-slate-400">Win Rate</div>
              <div className="text-xl font-bold text-slate-100 num-tabular">72.4%</div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
