import React, { useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  ShieldAlert,
  Activity,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { FinancialChart } from '../components/common/FinancialChart';
import { AICommitteeWidget } from '../components/common/AICommitteeWidget';
import { useWebSocket } from '../hooks/useWebSocket';
import { ErrorBoundary } from '../components/common/ErrorBoundary';

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
  const { tickerList } = useWebSocket();

  return (
    <div className="space-y-6 w-full max-w-full min-w-0">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#121826] p-5 rounded-2xl border border-[#1E293B] relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-full bg-gradient-to-l from-cyan-500/10 via-transparent to-transparent pointer-events-none" />

        <div className="relative z-10 space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              INSTITUTIONAL QUANT OS
            </span>
            <span className="text-xs font-mono text-slate-400">&bull; Live Market Telemetry</span>
          </div>
          <h1 className="text-2xl font-mono font-bold text-slate-100">
            Hedge Fund Command Center
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Real-time algorithmic trading, multi-agent AI committee, and portfolio risk telemetry.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <div className="bg-[#0D121F] px-4 py-2 rounded-xl border border-[#1E293B] text-right">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Engine Status</div>
            <div className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5 justify-end">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              NSE Live Stream Active
            </div>
          </div>
        </div>
      </div>

      {/* Realtime Indices Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {(tickerList.length > 0 ? tickerList.slice(0, 4) : [
          { ticker: 'NIFTY.NSE', name: 'NIFTY 50', price: 24350.50, change: 125.40, change_percent: 0.52 },
          { ticker: 'BANKNIFTY.NSE', name: 'NIFTY BANK', price: 52180.20, change: -180.30, change_percent: -0.34 },
          { ticker: 'RELIANCE.NSE', name: 'Reliance', price: 2980.45, change: 32.10, change_percent: 1.09 },
          { ticker: 'TCS.NSE', name: 'TCS', price: 4250.80, change: -15.20, change_percent: -0.36 },
        ]).map((idx) => {
          const isUp = idx.change >= 0;
          return (
            <div
              key={idx.ticker}
              className="bg-[#121826] p-3 rounded-xl border border-[#1E293B] flex items-center justify-between min-w-0"
            >
              <div className="truncate pr-2">
                <div className="text-xs font-mono font-bold text-slate-300 truncate">{idx.name}</div>
                <div className="text-sm font-mono font-bold text-slate-100 num-tabular mt-0.5">
                  ₹{idx.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>
              <div
                className={`text-xs font-mono font-semibold px-2 py-1 rounded flex items-center gap-1 shrink-0 ${
                  isUp ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40' : 'bg-red-950/60 text-red-400 border border-red-800/40'
                }`}
              >
                {isUp ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                {isUp ? '+' : ''}
                {idx.change_percent.toFixed(2)}%
              </div>
            </div>
          );
        })}
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
        <div className="lg:col-span-2 space-y-6 min-w-0">
          <ErrorBoundary fallbackTitle="Chart Error">
            <FinancialChart data={sampleChartData} symbol={activeSymbol} height={360} />
          </ErrorBoundary>

          {/* Top Ticker Screener Data Table */}
          <div className="bg-[#121826] rounded-xl p-5 border border-[#1E293B] space-y-3 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
              <h3 className="font-mono font-bold text-sm text-slate-100 flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                Live Focus Watchlist & Signals
              </h3>
              <span className="text-xs font-mono text-slate-400">WebSocket Stream</span>
            </div>

            <div className="overflow-x-auto min-w-0">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-[#1E293B] pb-2 uppercase text-[10px]">
                    <th className="pb-2">Symbol</th>
                    <th className="pb-2">Exchange</th>
                    <th className="pb-2 text-right">Price</th>
                    <th className="pb-2 text-right">24h Change</th>
                    <th className="pb-2 text-right">AI Consensus Signal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1E293B]/60 text-slate-200">
                  {(tickerList.length > 0 ? tickerList : [
                    { ticker: 'RELIANCE.NSE', name: 'Reliance', price: 2980.45, change_percent: 1.09 },
                    { ticker: 'TCS.NSE', name: 'TCS', price: 4250.80, change_percent: -0.36 },
                    { ticker: 'INFY.NSE', name: 'Infosys', price: 1820.60, change_percent: 0.80 },
                    { ticker: 'HDFCBANK.NSE', name: 'HDFC Bank', price: 1640.25, change_percent: 0.54 },
                  ]).map((item) => {
                    const isUp = item.change_percent >= 0;
                    const cleanSym = item.ticker.split('.')[0];
                    return (
                      <tr
                        key={item.ticker}
                        onClick={() => setActiveSymbol(cleanSym)}
                        className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                      >
                        <td className="py-3 font-bold text-slate-100">{cleanSym}</td>
                        <td className="py-3 text-slate-400">NSE</td>
                        <td className="py-3 text-right num-tabular font-bold">
                          ₹{item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                        <td
                          className={`py-3 text-right num-tabular font-semibold ${
                            isUp ? 'text-emerald-400' : 'text-red-400'
                          }`}
                        >
                          {isUp ? '+' : ''}
                          {item.change_percent.toFixed(2)}%
                        </td>
                        <td className="py-3 text-right">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              isUp
                                ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                                : 'bg-red-950/80 text-red-300 border border-red-800/60'
                            }`}
                          >
                            {isUp ? 'BUY' : 'HOLD'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* AI Committee Widget Sidebar Column */}
        <div className="space-y-6 min-w-0">
          <ErrorBoundary fallbackTitle="AI Committee Error">
            <AICommitteeWidget />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
};
