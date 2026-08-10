import React, { useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  ShieldAlert,
  Activity,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { FinancialChart } from '../components/common/FinancialChart';
import { AICommitteeWidget } from '../components/common/AICommitteeWidget';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMarketHistory } from '../hooks/useMarketData';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { Skeleton } from '../components/common/Skeleton';

export const DashboardPage: React.FC = () => {
  const [activeSymbol, setActiveSymbol] = useState('RELIANCE');
  const { tickerList, isLoading: wsLoading } = useWebSocket();
  const { data: chartData, isLoading: chartLoading } = useMarketHistory(activeSymbol);

  return (
    <div className="flex flex-col gap-6 w-full max-w-full min-w-0">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#121826] p-5 rounded-2xl border border-[#1E293B]">
        <div className="space-y-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              INSTITUTIONAL QUANT OS
            </span>
            <span className="text-xs font-mono text-slate-400">&bull; Live Market Telemetry</span>
          </div>
          <h1 className="text-2xl font-mono font-bold text-slate-100 truncate">
            Hedge Fund Command Center
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Real-time algorithmic trading, multi-agent AI committee, and portfolio risk telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="bg-[#0D121F] px-4 py-2 rounded-xl border border-[#1E293B] text-right">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Engine Status</div>
            <div className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5 justify-end">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              NSE Live Stream Active
            </div>
          </div>
        </div>
      </div>

      {/* Realtime Indices Summary Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full">
        {wsLoading || tickerList.length === 0
          ? Array.from({ length: 4 }).map((_, idx) => (
              <div
                key={idx}
                className="bg-[#121826] p-3 rounded-xl border border-[#1E293B] space-y-2"
              >
                <Skeleton width={80} height={14} />
                <Skeleton width={110} height={20} />
              </div>
            ))
          : tickerList.slice(0, 4).map((idx) => {
              const isUp = idx.change >= 0;
              return (
                <div
                  key={idx.ticker}
                  className="bg-[#121826] p-3 rounded-xl border border-[#1E293B] flex items-center justify-between min-w-0"
                >
                  <div className="truncate pr-2">
                    <div className="text-xs font-mono font-bold text-slate-300 truncate">
                      {idx.name || idx.ticker.split('.')[0]}
                    </div>
                    <div className="text-sm font-mono font-bold text-slate-100 num-tabular mt-0.5">
                      ₹{idx.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                  <div
                    className={`text-xs font-mono font-semibold px-2 py-1 rounded flex items-center gap-1 shrink-0 ${
                      isUp
                        ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40'
                        : 'bg-red-950/60 text-red-400 border border-red-800/40'
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">
        <div className="lg:col-span-2 flex flex-col gap-6 min-w-0 w-full">
          <ErrorBoundary fallbackTitle="Chart Error">
            <FinancialChart
              data={chartData || []}
              symbol={activeSymbol}
              height={360}
              isLoading={chartLoading}
            />
          </ErrorBoundary>

          {/* Live Focus Watchlist Table */}
          <div className="bg-[#121826] rounded-xl p-5 border border-[#1E293B] space-y-3 min-w-0 w-full">
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
              <h3 className="font-mono font-bold text-sm text-slate-100 flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                Live Focus Watchlist & Signals
              </h3>
              <span className="text-xs font-mono text-slate-400">WebSocket Live Stream</span>
            </div>

            <div className="overflow-x-auto min-w-0 w-full">
              <table className="w-full text-left font-mono text-xs min-w-[500px]">
                <thead>
                  <tr className="text-slate-400 border-b border-[#1E293B] pb-2 uppercase text-[10px]">
                    <th className="pb-2">Symbol</th>
                    <th className="pb-2">Exchange</th>
                    <th className="pb-2 text-right">Price</th>
                    <th className="pb-2 text-right">24h Change</th>
                    <th className="pb-2 text-right">AI Signal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1E293B]/60 text-slate-200">
                  {tickerList.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-500">
                        Connecting to live backend stream...
                      </td>
                    </tr>
                  ) : (
                    tickerList.map((item) => {
                      const isUp = item.change_percent >= 0;
                      const cleanSym = item.ticker.split('.')[0];
                      return (
                        <tr
                          key={item.ticker}
                          onClick={() => setActiveSymbol(cleanSym)}
                          className={`hover:bg-slate-800/50 cursor-pointer transition-colors ${
                            activeSymbol === cleanSym ? 'bg-cyan-950/40 font-semibold' : ''
                          }`}
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
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* AI Committee Sidebar Column */}
        <div className="flex flex-col gap-6 min-w-0 w-full">
          <ErrorBoundary fallbackTitle="AI Committee Error">
            <AICommitteeWidget />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
};
