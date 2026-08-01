import React, { useState } from 'react';
import { Building2, Search, TrendingUp, BarChart2, ShieldCheck, FileText, CheckCircle2 } from 'lucide-react';
import { FinancialChart } from '../components/common/FinancialChart';
import { StatCard } from '../components/common/StatCard';
import { motion } from 'framer-motion';

const sampleChartData = [
  { date: '2026-07-01', open: 6100.0, high: 6250.0, low: 6050.0, close: 6200.0, volume: 1200000 },
  { date: '2026-07-10', open: 6200.0, high: 6380.0, low: 6180.0, close: 6350.0, volume: 1540000 },
  { date: '2026-07-20', open: 6350.0, high: 6450.0, low: 6300.0, close: 6410.0, volume: 1800000 },
  { date: '2026-07-31', open: 6410.0, high: 6520.0, low: 6390.0, close: 6420.0, volume: 1950000 },
];

export const CompanyAnalysisPage: React.FC = () => {
  const [symbol, setSymbol] = useState('TRENT');
  const [searchInput, setSearchInput] = useState('TRENT');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setSymbol(searchInput.trim().toUpperCase());
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono"
    >
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <Building2 className="h-4 w-4" />
            <span>DEEP CORPORATE INTELLIGENCE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">{symbol} — Fundamental & Quant Analysis</h1>
          <p className="text-xs text-slate-400">Institutional SEC/NSE financial ratios, balance sheet health, and valuation metrics.</p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Enter symbol (e.g. TRENT, RELIANCE)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-64"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold"
          >
            Analyze
          </button>
        </form>
      </div>

      {/* Ratios Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="P/E Ratio (TTM)" value="82.4" subtext="Industry Median: 64.2" icon={BarChart2} />
        <StatCard title="ROCE %" value="24.8%" change={3.2} changeLabel="YoY expansion" icon={TrendingUp} />
        <StatCard title="Debt / Equity" value="0.32" subtext="Low leverage risk" icon={ShieldCheck} />
        <StatCard title="Market Cap" value="₹228,450 Cr" subtext="NSE Large Cap" icon={Building2} />
      </div>

      {/* Main Grid Chart + Filings AI Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <FinancialChart data={sampleChartData} symbol={symbol} height={380} />

          {/* Quarterly Earnings & Growth Table */}
          <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <FileText className="h-4 w-4 text-cyan-400" />
              Quarterly Financial Performance (₹ Cr)
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-white/5">
                    <th className="pb-3">Metric</th>
                    <th className="pb-3 text-right">Q1 2026</th>
                    <th className="pb-3 text-right">Q4 2025</th>
                    <th className="pb-3 text-right">Q3 2025</th>
                    <th className="pb-3 text-right">YoY Growth</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-200">
                  {[
                    { m: 'Net Revenue', q1: '₹4,120', q4: '₹3,850', q3: '₹3,520', yoy: '+24.5%' },
                    { m: 'EBITDA', q1: '₹680', q4: '₹610', q3: '₹540', yoy: '+28.2%' },
                    { m: 'Net Profit (PAT)', q1: '₹420', q4: '₹375', q3: '₹320', yoy: '+31.25%' },
                    { m: 'EPS (₹)', q1: '₹11.82', q4: '₹10.55', q3: '₹9.01', yoy: '+31.18%' },
                  ].map((row) => (
                    <tr key={row.m} className="hover:bg-white/5 transition-colors">
                      <td className="py-3 font-bold text-slate-100">{row.m}</td>
                      <td className="py-3 text-right num-tabular text-slate-200 font-bold">{row.q1}</td>
                      <td className="py-3 text-right num-tabular text-slate-400">{row.q4}</td>
                      <td className="py-3 text-right num-tabular text-slate-400">{row.q3}</td>
                      <td className="py-3 text-right num-tabular font-bold text-emerald-400">{row.yoy}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* AI Fundamental Insights Sidebar */}
        <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="font-bold text-sm text-slate-100">AI Fundamental Audit Summary</h3>
            <span className="text-xs text-emerald-400 font-bold">HEALTHY</span>
          </div>

          <div className="space-y-3 text-xs">
            {[
              { title: 'Store Footprint Expansion', desc: 'Zudio store count expanded by 42 locations in Q1, driving retail sales growth.' },
              { title: 'Working Capital Efficiency', desc: 'Inventory turnover ratio improved from 4.2x to 5.1x, freeing cash flow.' },
              { title: 'Valuation Premium Guard', desc: 'Trading at 82x P/E; risk officer recommends trailing stop-loss at ₹6,150.' },
            ].map((item, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                <div className="flex items-center gap-2 font-bold text-slate-200">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>{item.title}</span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed pl-6">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
