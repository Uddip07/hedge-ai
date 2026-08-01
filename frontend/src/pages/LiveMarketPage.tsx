import React, { useState } from 'react';
import { TrendingUp, Search, Filter, RefreshCw, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react';
import { FinancialChart } from '../components/common/FinancialChart';
import { motion } from 'framer-motion';

export const LiveMarketPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('ALL');
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE');

  const stocks = [
    { symbol: 'RELIANCE', name: 'Reliance Industries Ltd.', sector: 'Energy', price: 2638.5, change: +2.15, volume: '3.2M', mcap: 'Large Cap' },
    { symbol: 'TRENT', name: 'Trent Limited', sector: 'Retail', price: 6420.0, change: +4.80, volume: '1.8M', mcap: 'Large Cap' },
    { symbol: 'DELHIVERY', name: 'Delhivery Limited', sector: 'Logistics', price: 412.3, change: -1.20, volume: '890K', mcap: 'Mid Cap' },
    { symbol: 'INFY', name: 'Infosys Limited', sector: 'IT', price: 1820.75, change: +0.45, volume: '2.1M', mcap: 'Large Cap' },
    { symbol: 'TATAMOTORS', name: 'Tata Motors Ltd.', sector: 'Auto', price: 1045.0, change: +1.95, volume: '4.5M', mcap: 'Large Cap' },
    { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd.', sector: 'Banking', price: 1612.4, change: +0.85, volume: '5.6M', mcap: 'Large Cap' },
    { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd.', sector: 'Banking', price: 1240.2, change: +1.10, volume: '4.1M', mcap: 'Large Cap' },
    { symbol: 'ATGL', name: 'Adani Total Gas', sector: 'Energy', price: 890.5, change: -2.35, volume: '1.1M', mcap: 'Mid Cap' },
  ];

  const filteredStocks = stocks.filter((s) => {
    const matchesSearch = s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || s.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSector = selectedSector === 'ALL' || s.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono"
    >
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <TrendingUp className="h-4 w-4" />
            <span>REALTIME MARKET SCREENER</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Live Indian Markets (NSE/BSE)</h1>
          <p className="text-xs text-slate-400">Institutional depth of market, sector heatmaps, and price history feeds.</p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search Symbol / Company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-64"
            />
          </div>

          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
          >
            <option value="ALL" className="bg-slate-900">All Sectors</option>
            <option value="Banking" className="bg-slate-900">Banking</option>
            <option value="Energy" className="bg-slate-900">Energy</option>
            <option value="IT" className="bg-slate-900">IT</option>
            <option value="Retail" className="bg-slate-900">Retail</option>
            <option value="Auto" className="bg-slate-900">Auto</option>
          </select>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table Left Column */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Layers className="h-4 w-4 text-cyan-400" />
              Symbol Screener Matrix ({filteredStocks.length} tickers)
            </h3>
            <span className="text-xs text-slate-400">Live Auto-Scan</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-white/5">
                  <th className="pb-3">Symbol</th>
                  <th className="pb-3">Company Name</th>
                  <th className="pb-3">Sector</th>
                  <th className="pb-3 text-right">Price</th>
                  <th className="pb-3 text-right">Change</th>
                  <th className="pb-3 text-right">Volume</th>
                  <th className="pb-3 text-right">Cap</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-200">
                {filteredStocks.map((s) => (
                  <tr
                    key={s.symbol}
                    onClick={() => setSelectedSymbol(s.symbol)}
                    className={`hover:bg-white/5 cursor-pointer transition-colors ${
                      selectedSymbol === s.symbol ? 'bg-cyan-500/10 font-semibold' : ''
                    }`}
                  >
                    <td className="py-3 font-bold text-slate-100">{s.symbol}</td>
                    <td className="py-3 text-slate-300">{s.name}</td>
                    <td className="py-3 text-slate-400">{s.sector}</td>
                    <td className="py-3 text-right num-tabular font-bold">₹{s.price.toFixed(2)}</td>
                    <td className={`py-3 text-right num-tabular font-semibold ${s.change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {s.change >= 0 ? '+' : ''}{s.change.toFixed(2)}%
                    </td>
                    <td className="py-3 text-right num-tabular text-slate-400">{s.volume}</td>
                    <td className="py-3 text-right text-slate-400">{s.mcap}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column Depth of Market & Quick Details */}
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-bold text-sm text-slate-100">Depth of Market (L2 Orderbook)</h3>
              <span className="text-xs text-cyan-400">{selectedSymbol}</span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              {/* Bids */}
              <div className="space-y-1">
                <div className="text-emerald-400 font-bold border-b border-white/5 pb-1">Bids (Buy)</div>
                {[
                  { p: 2638.5, q: 1250 },
                  { p: 2638.0, q: 2400 },
                  { p: 2637.5, q: 3100 },
                ].map((b, i) => (
                  <div key={i} className="flex justify-between text-slate-300">
                    <span className="num-tabular font-bold">₹{b.p}</span>
                    <span className="text-slate-500 num-tabular">{b.q}</span>
                  </div>
                ))}
              </div>

              {/* Asks */}
              <div className="space-y-1">
                <div className="text-rose-400 font-bold border-b border-white/5 pb-1">Asks (Sell)</div>
                {[
                  { p: 2639.0, q: 950 },
                  { p: 2639.5, q: 1800 },
                  { p: 2640.0, q: 4200 },
                ].map((a, i) => (
                  <div key={i} className="flex justify-between text-slate-300">
                    <span className="num-tabular font-bold">₹{a.p}</span>
                    <span className="text-slate-500 num-tabular">{a.q}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
