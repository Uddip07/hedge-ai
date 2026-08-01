import React, { useState } from 'react';
import { PieChart, ShieldAlert, DollarSign, ArrowUpRight, ArrowDownRight, Zap, CheckCircle2 } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { motion } from 'framer-motion';

export const PortfolioPage: React.FC = () => {
  const [orderType, setOrderType] = useState<'BUY' | 'SELL'>('BUY');
  const [symbolInput, setSymbolInput] = useState('TRENT');
  const [qtyInput, setQtyInput] = useState('25');
  const [orderExecuted, setOrderExecuted] = useState(false);

  const holdings = [
    { symbol: 'RELIANCE', qty: 100, avgPrice: 2450.0, currentPrice: 2638.5, pnl: +18850, pnlPct: +7.69, sector: 'Energy' },
    { symbol: 'TRENT', qty: 50, avgPrice: 5800.0, currentPrice: 6420.0, pnl: +31000, pnlPct: +10.68, sector: 'Retail' },
    { symbol: 'INFY', qty: 200, avgPrice: 1750.0, currentPrice: 1820.75, pnl: +14150, pnlPct: +4.04, sector: 'IT' },
    { symbol: 'DELHIVERY', qty: 300, avgPrice: 425.0, currentPrice: 412.3, pnl: -3810, pnlPct: -2.98, sector: 'Logistics' },
  ];

  const totalValue = holdings.reduce((acc, h) => acc + h.qty * h.currentPrice, 0);
  const totalPnL = holdings.reduce((acc, h) => acc + h.pnl, 0);

  const handleExecuteOrder = (e: React.FormEvent) => {
    e.preventDefault();
    setOrderExecuted(true);
    setTimeout(() => setOrderExecuted(false), 3000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono"
    >
      {/* Header */}
      <div className="flex items-center justify-between glass-panel p-5 rounded-2xl">
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
        <StatCard title="Total Portfolio Value" value={`₹${totalValue.toLocaleString('en-IN')}`} change={4.2} changeLabel="overall gain" icon={DollarSign} />
        <StatCard title="Unrealized P&L" value={`₹${totalPnL.toLocaleString('en-IN')}`} change={6.8} changeLabel="unrealized" icon={PieChart} />
        <StatCard title="Portfolio Beta" value="0.88" subtext="Benchmark: NIFTY 50" icon={ShieldAlert} />
        <StatCard title="Value at Risk (VaR 95%)" value="₹124,500" subtext="1-Day Max Potential Loss" icon={ShieldAlert} />
      </div>

      {/* Main Grid: Holdings + Order Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Holdings Table */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="font-bold text-sm text-slate-100">Active Open Positions ({holdings.length})</h3>
            <span className="text-xs text-emerald-400 font-semibold">Live Mark-to-Market</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-white/5">
                  <th className="pb-3">Symbol</th>
                  <th className="pb-3 text-right">Qty</th>
                  <th className="pb-3 text-right">Avg Price</th>
                  <th className="pb-3 text-right">Current</th>
                  <th className="pb-3 text-right">P&L (₹)</th>
                  <th className="pb-3 text-right">P&L (%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-200">
                {holdings.map((h) => (
                  <tr key={h.symbol} className="hover:bg-white/5 transition-colors">
                    <td className="py-3 font-bold text-slate-100">{h.symbol}</td>
                    <td className="py-3 text-right num-tabular text-slate-300">{h.qty}</td>
                    <td className="py-3 text-right num-tabular text-slate-400">₹{h.avgPrice.toFixed(2)}</td>
                    <td className="py-3 text-right num-tabular font-bold">₹{h.currentPrice.toFixed(2)}</td>
                    <td className={`py-3 text-right num-tabular font-bold ${h.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      ₹{h.pnl.toLocaleString('en-IN')}
                    </td>
                    <td className={`py-3 text-right num-tabular font-semibold ${h.pnlPct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {h.pnlPct >= 0 ? '+' : ''}{h.pnlPct.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Paper Order Execution Panel */}
        <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Zap className="h-4 w-4 text-cyan-400" />
              Paper Order Execution
            </h3>
            <span className="text-xs text-slate-400">INSTANT FILL</span>
          </div>

          <form onSubmit={handleExecuteOrder} className="space-y-4">
            {/* Side Selector */}
            <div className="grid grid-cols-2 gap-2 bg-white/5 p-1 rounded-xl border border-white/5">
              <button
                type="button"
                onClick={() => setOrderType('BUY')}
                className={`py-2 rounded-lg font-bold text-xs transition-all ${
                  orderType === 'BUY' ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                BUY
              </button>
              <button
                type="button"
                onClick={() => setOrderType('SELL')}
                className={`py-2 rounded-lg font-bold text-xs transition-all ${
                  orderType === 'SELL' ? 'bg-rose-500 text-slate-100 shadow' : 'text-slate-400 hover:text-slate-200'
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
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs font-bold text-slate-100 focus:outline-none focus:border-cyan-500/50"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs text-slate-400">Quantity</label>
              <input
                type="number"
                value={qtyInput}
                onChange={(e) => setQtyInput(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs font-bold text-slate-100 focus:outline-none focus:border-cyan-500/50"
              />
            </div>

            <button
              type="submit"
              className={`w-full py-3 rounded-xl font-bold text-xs transition-all shadow-lg ${
                orderType === 'BUY'
                  ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-950/50'
                  : 'bg-rose-500 hover:bg-rose-400 text-slate-100 shadow-rose-950/50'
              }`}
            >
              EXECUTE {orderType} ORDER
            </button>

            {orderExecuted && (
              <motion.div
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2"
              >
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>Paper Order for {qtyInput} {symbolInput} executed at Market Price!</span>
              </motion.div>
            )}
          </form>
        </div>
      </div>
    </motion.div>
  );
};
