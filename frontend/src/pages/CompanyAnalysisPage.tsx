import React, { useState } from 'react';
import { Building2, Search, TrendingUp, BarChart2, ShieldCheck, FileText, CheckCircle2 } from 'lucide-react';
import { FinancialChart } from '../components/common/FinancialChart';
import { StatCard } from '../components/common/StatCard';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { useMarketHistory } from '../hooks/useMarketData';

export const CompanyAnalysisPage: React.FC = () => {
  const [symbol, setSymbol] = useState('TRENT');
  const [searchInput, setSearchInput] = useState('TRENT');

  const { data: chartData, isLoading: chartLoading } = useMarketHistory(symbol);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setSymbol(searchInput.trim().toUpperCase());
    }
  };

  return (
    <div className="space-y-6 w-full max-w-full min-w-0 font-mono">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#121826] p-5 rounded-2xl border border-[#1E293B]">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <Building2 className="h-4 w-4" />
            <span>DEEP CORPORATE INTELLIGENCE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">{symbol} — Fundamental & Quant Analysis</h1>
          <p className="text-xs text-slate-400">
            Institutional SEC/NSE financial ratios, balance sheet health, and valuation metrics.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Enter symbol (e.g. TRENT, RELIANCE)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="bg-slate-900 border border-[#1E293B] rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-56 md:w-64"
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
        <div className="lg:col-span-2 space-y-6 min-w-0">
          <ErrorBoundary fallbackTitle="Financial Chart Error">
            <FinancialChart
              data={chartData || []}
              symbol={symbol}
              height={360}
              isLoading={chartLoading}
            />
          </ErrorBoundary>

          {/* Quarterly Earnings & Growth Table */}
          <div className="bg-[#121826] rounded-2xl p-5 border border-[#1E293B] space-y-4 min-w-0">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <FileText className="h-4 w-4 text-cyan-400" />
              Quarterly Financial Performance (₹ Cr)
            </h3>

            <div className="overflow-x-auto min-w-0">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-[#1E293B] uppercase text-[10px]">
                    <th className="pb-3">Metric</th>
                    <th className="pb-3 text-right">Q1 2026</th>
                    <th className="pb-3 text-right">Q4 2025</th>
                    <th className="pb-3 text-right">Q3 2025</th>
                    <th className="pb-3 text-right">YoY Growth</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1E293B]/60 text-slate-200">
                  {[
                    { m: 'Net Revenue', q1: '₹4,120', q4: '₹3,850', q3: '₹3,520', yoy: '+24.5%' },
                    { m: 'EBITDA', q1: '₹680', q4: '₹610', q3: '₹540', yoy: '+28.2%' },
                    { m: 'Net Profit (PAT)', q1: '₹420', q4: '₹375', q3: '₹320', yoy: '+31.25%' },
                    { m: 'EPS (₹)', q1: '₹11.82', q4: '₹10.55', q3: '₹9.01', yoy: '+31.18%' },
                  ].map((row) => (
                    <tr key={row.m} className="hover:bg-slate-800/50 transition-colors">
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
        <div className="bg-[#121826] rounded-2xl p-5 border border-[#1E293B] space-y-4 min-w-0">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="font-bold text-sm text-slate-100">AI Fundamental Audit Summary</h3>
            <span className="text-xs text-emerald-400 font-bold">HEALTHY</span>
          </div>

          <div className="space-y-3 text-xs">
            {[
              {
                title: 'Store Footprint Expansion',
                desc: 'Zudio store count expanded by 42 locations in Q1, driving retail sales growth.',
              },
              {
                title: 'Working Capital Efficiency',
                desc: 'Inventory turnover ratio improved from 4.2x to 5.1x, freeing cash flow.',
              },
              {
                title: 'Valuation Premium Guard',
                desc: 'Trading at 82x P/E; risk officer recommends trailing stop-loss at ₹6,150.',
              },
            ].map((item, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-[#1E293B] space-y-1">
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
    </div>
  );
};
