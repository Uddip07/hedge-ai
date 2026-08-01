import React, { useState } from 'react';
import { PieChart, ShieldAlert, DollarSign, Zap, CheckCircle2 } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { toast } from '../hooks/useToast';
import { ErrorBoundary } from '../components/common/ErrorBoundary';

export const PortfolioPage: React.FC = () => {
  const [orderType, setOrderType] = useState<'BUY' | 'SELL'>('BUY');
  const [symbolInput, setSymbolInput] = useState('TRENT');
  const [qtyInput, setQtyInput] = useState('25');
  const [orderExecuted, setOrderExecuted] = useState(false);

  const holdings = [
    { symbol: 'RELIANCE', qty: 100, avgPrice: 2450.0, currentPrice: 2980.45, pnl: +53045, pnlPct: +21.65, sector: 'Energy' },
    { symbol: 'TRENT', qty: 50, avgPrice: 5800.0, currentPrice: 6420.0, pnl: +31000, pnlPct: +10.68, sector: 'Retail' },
    { symbol: 'INFY', qty: 200, avgPrice: 1750.0, currentPrice: 1820.60, pnl: +14120, pnlPct: +4.03, sector: 'IT' },
    { symbol: 'DELHIVERY', qty: 300, avgPrice: 425.0, currentPrice: 412.3, pnl: -3810, pnlPct: -2.98, sector: 'Logistics' },
  ];

  const totalValue = holdings.reduce((acc, h) => acc + h.qty * h.currentPrice, 0);
  const totalPnL = holdings.reduce((acc, h) => acc + h.pnl, 0);

  const handleExecuteOrder = (e: React.FormEvent) => {
    e.preventDefault();
    setOrderExecuted(true);
    toast.success(
      'Order Executed Successfully',
      `Paper ${orderType} order for ${qtyInput} shares of ${symbolInput} filled.`
    );
    setTimeout(() => setOrderExecuted(false), 3000);
  };

  return (
    <div className="space-y-6 w-full max-w-full min-w-0 font-mono">
      {/* Header */}
      <div className="flex items-center justify-between bg-[#121826] p-5 rounded-2xl border border-[#1E293B]">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <PieChart className="h-4 w-4" />
            <span>PORTFOLIO TELEMETRY & RISK ENGINE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Institutional Portfolio Analytics</h1>
          <p className="text-xs text-slate-400">Position allocations, Risk Metrics (VaR), and Paper Trading execution.</p>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Portfolio Value"
          value={`₹${totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          change={4.2}
          changeLabel="overall gain"
          icon={DollarSign}
        />
        <StatCard
          title="Unrealized P&L"
          value={`₹${totalPnL.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          change={6.8}
          changeLabel="unrealized"
          icon={PieChart}
        />
        <StatCard
          title="Portfolio Beta"
          value="0.88"
          subtext="Benchmark: NIFTY 50"
          icon={ShieldAlert}
        />
        <StatCard
          title="Value at Risk (VaR 95%)"
          value="₹124,500"
          subtext="1-Day Max Potential Loss"
          icon={ShieldAlert}
        />
      </div>

      {/* Main Grid: Holdings + Order Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Holdings Table */}
        <div className="lg:col-span-2 bg-[#121826] rounded-2xl p-5 border border-[#1E293B] space-y-4 min-w-0">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="font-bold text-sm text-slate-100">Active Open Positions ({holdings.length})</h3>
            <span className="text-xs text-emerald-400 font-semibold">Live Mark-to-Market</span>
          </div>

          <div className="overflow-x-auto min-w-0">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-[#1E293B] uppercase text-[10px]">
                  <th className="pb-3">Symbol</th>
                  <th className="pb-3 text-right">Qty</th>
                  <th className="pb-3 text-right">Avg Price</th>
                  <th className="pb-3 text-right">Current</th>
                  <th className="pb-3 text-right">P&L (₹)</th>
                  <th className="pb-3 text-right">P&L (%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B]/60 text-slate-200">
                {holdings.map((h) => (
                  <tr key={h.symbol} className="hover:bg-slate-800/50 transition-colors">
                    <td className="py-3 font-bold text-slate-100">{h.symbol}</td>
                    <td className="py-3 text-right num-tabular text-slate-300">{h.qty}</td>
                    <td className="py-3 text-right num-tabular text-slate-400">₹{h.avgPrice.toFixed(2)}</td>
                    <td className="py-3 text-right num-tabular font-bold">₹{h.currentPrice.toFixed(2)}</td>
                    <td
                      className={`py-3 text-right num-tabular font-bold ${
                        h.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}
                    >
                      ₹{h.pnl.toLocaleString('en-IN')}
                    </td>
                    <td
                      className={`py-3 text-right num-tabular font-semibold ${
                        h.pnlPct >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}
                    >
                      {h.pnlPct >= 0 ? '+' : ''}
                      {h.pnlPct.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Paper Order Execution Panel */}
        <div className="bg-[#121826] rounded-2xl p-5 border border-[#1E293B] space-y-4 min-w-0">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Zap className="h-4 w-4 text-cyan-400" />
              Paper Order Execution
            </h3>
            <span className="text-xs text-slate-400">INSTANT FILL</span>
          </div>

          <ErrorBoundary fallbackTitle="Order Form Error">
            <form onSubmit={handleExecuteOrder} className="space-y-4">
              {/* Side Selector */}
              <div className="grid grid-cols-2 gap-2 bg-slate-900 p-1 rounded-xl border border-[#1E293B]">
                <button
                  type="button"
                  onClick={() => setOrderType('BUY')}
                  className={`py-2 rounded-lg font-bold text-xs transition-all ${
                    orderType === 'BUY'
                      ? 'bg-emerald-500 text-slate-950 shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  BUY
                </button>
                <button
                  type="button"
                  onClick={() => setOrderType('SELL')}
                  className={`py-2 rounded-lg font-bold text-xs transition-all ${
                    orderType === 'SELL'
                      ? 'bg-red-500 text-slate-100 shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  SELL
                </button>
              </div>

              <div className="space-y-2">
                <label className="text-xs text-slate-400">Ticker Symbol</label>
                <input
                  type="text"
                  value={symbolInput}
                  onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
                  className="w-full bg-slate-900 border border-[#1E293B] rounded-xl px-3 py-2 text-xs font-bold text-slate-100 focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs text-slate-400">Quantity</label>
                <input
                  type="number"
                  value={qtyInput}
                  onChange={(e) => setQtyInput(e.target.value)}
                  className="w-full bg-slate-900 border border-[#1E293B] rounded-xl px-3 py-2 text-xs font-bold text-slate-100 focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              <button
                type="submit"
                className={`w-full py-3 rounded-xl font-bold text-xs transition-all shadow-lg ${
                  orderType === 'BUY'
                    ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-950/50'
                    : 'bg-red-500 hover:bg-red-400 text-slate-100 shadow-red-950/50'
                }`}
              >
                EXECUTE {orderType} ORDER
              </button>

              {orderExecuted && (
                <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-800/40 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>
                    Paper Order for {qtyInput} {symbolInput} executed at Market Price!
                  </span>
                </div>
              )}
            </form>
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
};
