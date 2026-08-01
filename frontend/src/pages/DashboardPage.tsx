import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  ShieldAlert,
  Zap,
  Activity,
  Layers,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { FinancialChart } from '../components/common/FinancialChart';
import { AICommitteeWidget } from '../components/common/AICommitteeWidget';
import { motion } from 'framer-motion';

// Mock price series for chart
const sampleChartData = [
  { date: '2026-07-01', open: 2450.0, high: 2480.0, low: 2440.0, close: 2475.5, volume: 1450000 },
  { date: '2026-07-05', open: 2475.5, high: 2510.0, low: 2470.0, close: 2505.0, volume: 1890000 },
  { date: '2026-07-10', open: 2505.0, high: 2525.0, low: 2490.0, close: 2495.0, volume: 1230000 },
  { date: '2026-07-15', open: 2495.0, high: 2540.0, low: 2490.0, close: 2535.0, volume: 2100000 },
  { date: '2026-07-20', open: 2535.0, high: 2580.0, low: 2530.0, close: 2570.0, volume: 2450000 },
  { date: '2026-07-25', open: 2570.0, high: 2610.0, low: 2565.0, close: 2605.0, volume: 2900000 },
  { date: '2026-07-31', open: 2605.0, high: 2645.0, low: 2600.0, close: 2638.5, volume: 3200000 },
];

export const DashboardPage: React.FC = () => {
  const [activeSymbol, setActiveSymbol] = useState('RELIANCE');

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6 space-y-6 max-w-[1600px] mx-auto"
    >
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-cyan-500/20 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-full bg-gradient-to-l from-cyan-500/10 via-transparent to-transparent pointer-events-none" />

        <div className="relative z-10 space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              INSTITUTIONAL QUANT OS
            </span>
            <span className="text-xs font-mono text-slate-400">&bull; Live Market Feeds</span>
          </div>
          <h1 className="text-2xl font-mono font-bold text-slate-100">
            Hedge Fund Command Center
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Real-time algorithmic trading, multi-agent AI committee, and portfolio risk telemetry.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <div className="glass-panel px-4 py-2 rounded-xl border border-white/10 text-right">
            <div className="text-[10px] font-mono text-slate-400 uppercase">System Status</div>
            <div className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5 justify-end">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
              NSE Realtime Active
            </div>
          </div>
        </div>
      </div>

      {/* Indices Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { symbol: 'NIFTY 50', value: '24,834.80', change: +0.65 },
          { symbol: 'BANK NIFTY', value: '52,140.25', change: +0.82 },
          { symbol: 'NIFTY IT', value: '40,210.15', change: -0.24 },
          { symbol: 'SENSEX', value: '81,420.90', change: +0.58 },
        ].map((idx) => (
          <div key={idx.symbol} className="glass-panel p-3 rounded-xl border border-white/5 flex items-center justify-between">
            <div>
              <div className="text-xs font-mono font-bold text-slate-300">{idx.symbol}</div>
              <div className="text-sm font-mono font-bold text-slate-100 num-tabular mt-0.5">{idx.value}</div>
            </div>
            <div className={`text-xs font-mono font-semibold px-2 py-1 rounded-md flex items-center gap-1 ${idx.change >= 0 ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}`}>
              {idx.change >= 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
              {idx.change >= 0 ? '+' : ''}{idx.change}%
            </div>
          </div>
        ))}
      </div>

      {/* Telemetry Stat Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Portfolio AUM"
          value="₹14,250,000"
          change={2.45}
          changeLabel="vs last week"
          icon={DollarSign}
        />
        <StatCard
          title="Daily Realized P&L"
          value="₹348,200"
          change={1.82}
          changeLabel="today"
          icon={TrendingUp}
        />
        <StatCard
          title="Strategy Win Rate"
          value="68.4%"
          change={0.5}
          changeLabel="120 trades"
          icon={Activity}
        />
        <StatCard
          title="Sharpe Ratio (1Y)"
          value="2.84"
          subtext="Max Drawdown: -4.12%"
          icon={ShieldAlert}
        />
      </div>

      {/* Main Grid: Chart + AI Committee */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <FinancialChart data={sampleChartData} symbol={activeSymbol} height={380} />

          {/* Top Ticker Screener Data Table */}
          <div className="glass-panel rounded-xl p-5 border border-white/10 space-y-3">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-mono font-bold text-sm text-slate-100 flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                Active Focus Watchlist & Signals
              </h3>
              <span className="text-xs font-mono text-slate-400">Live Prices</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-white/5 pb-2">
                    <th className="pb-2">Symbol</th>
                    <th className="pb-2">Exchange</th>
                    <th className="pb-2 text-right">Price</th>
                    <th className="pb-2 text-right">24h Change</th>
                    <th className="pb-2 text-right">Volume</th>
                    <th className="pb-2 text-right">AI Signal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-200">
                  {[
                    { sym: 'RELIANCE', name: 'Reliance Industries', price: '₹2,638.50', chg: +2.15, vol: '3.2M', sig: 'STRONG BUY' },
                    { sym: 'TRENT', name: 'Trent Limited', price: '₹6,420.00', chg: +4.80, vol: '1.8M', sig: 'BUY' },
                    { sym: 'DELHIVERY', name: 'Delhivery Ltd', price: '₹412.30', chg: -1.20, vol: '890K', sig: 'HOLD' },
                    { sym: 'INFY', name: 'Infosys Limited', price: '₹1,820.75', chg: +0.45, vol: '2.1M', sig: 'NEUTRAL' },
                    { sym: 'TATAMOTORS', name: 'Tata Motors', price: '₹1,045.00', chg: +1.95, vol: '4.5M', sig: 'STRONG BUY' },
                  ].map((row) => (
                    <tr
                      key={row.sym}
                      onClick={() => setActiveSymbol(row.sym)}
                      className="hover:bg-white/5 cursor-pointer transition-colors"
                    >
                      <td className="py-3 font-bold text-slate-100">{row.sym}</td>
                      <td className="py-3 text-slate-400">NSE</td>
                      <td className="py-3 text-right num-tabular font-bold">{row.price}</td>
                      <td className={`py-3 text-right num-tabular font-semibold ${row.chg >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {row.chg >= 0 ? '+' : ''}{row.chg}%
                      </td>
                      <td className="py-3 text-right num-tabular text-slate-400">{row.vol}</td>
                      <td className="py-3 text-right">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          row.sig.includes('BUY') ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-slate-800 text-slate-300'
                        }`}>
                          {row.sig}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* AI Committee Widget Sidebar Column */}
        <div className="space-y-6">
          <AICommitteeWidget />
        </div>
      </div>
    </motion.div>
  );
};
