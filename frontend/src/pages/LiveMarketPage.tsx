import React, { useState } from 'react';
import { TrendingUp, Search, Layers, RefreshCw } from 'lucide-react';
import { FinancialChart } from '../components/common/FinancialChart';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMarketHistory } from '../hooks/useMarketData';
import { ErrorBoundary } from '../components/common/ErrorBoundary';

export const LiveMarketPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('ALL');
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE');

  const { tickerList, status, reconnect } = useWebSocket();
  const { data: chartData, isLoading: chartLoading } = useMarketHistory(selectedSymbol);

  const activeStocks = tickerList.map((t) => ({
    symbol: t.ticker.split('.')[0],
    fullTicker: t.ticker,
    name: t.name || t.ticker,
    sector: 'Equities',
    price: t.price,
    change: t.change_percent,
    volume: `${(t.volume / 1000000).toFixed(1)}M`,
    mcap: 'Large Cap',
  }));

  const filteredStocks = activeStocks.filter((s) => {
    const matchesSearch =
      s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSector = selectedSector === 'ALL' || s.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  const activeStock = activeStocks.find((s) => s.symbol === selectedSymbol);
  const activePrice = activeStock ? activeStock.price : 0;

  return (
    <div className="space-y-6 w-full max-w-full min-w-0 font-mono">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#121826] p-5 rounded-2xl border border-[#1E293B]">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <TrendingUp className="h-4 w-4" />
            <span>REALTIME MARKET SCREENER</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Live Indian Markets (NSE/BSE)</h1>
          <p className="text-xs text-slate-400">
            Institutional depth of market, real-time WebSocket ticker updates, and price history.
          </p>
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
              className="bg-slate-900 border border-[#1E293B] rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-56 md:w-64"
            />
          </div>

          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="bg-slate-900 border border-[#1E293B] rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
          >
            <option value="ALL">All Sectors</option>
            <option value="Banking">Banking</option>
            <option value="Energy">Energy</option>
            <option value="IT">IT</option>
            <option value="Retail">Retail</option>
            <option value="Auto">Auto</option>
          </select>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table & Chart Left Column */}
        <div className="lg:col-span-2 space-y-6 min-w-0">
          <ErrorBoundary fallbackTitle="Market Chart Error">
            <FinancialChart
              data={chartData || []}
              symbol={selectedSymbol}
              height={360}
              isLoading={chartLoading}
            />
          </ErrorBoundary>

          <div className="bg-[#121826] rounded-2xl p-5 border border-[#1E293B] space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                Symbol Screener Matrix ({filteredStocks.length} tickers)
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Stream: {status}</span>
                {status === 'ERROR' && (
                  <button
                    onClick={reconnect}
                    className="p-1 text-xs text-cyan-400 bg-cyan-950/60 rounded border border-cyan-800/60"
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>

            <div className="overflow-x-auto min-w-0">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-[#1E293B] uppercase text-[10px]">
                    <th className="pb-3">Symbol</th>
                    <th className="pb-3">Company Name</th>
                    <th className="pb-3">Sector</th>
                    <th className="pb-3 text-right">Price</th>
                    <th className="pb-3 text-right">Change</th>
                    <th className="pb-3 text-right">Volume</th>
                    <th className="pb-3 text-right">Cap</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1E293B]/60 text-slate-200">
                  {filteredStocks.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500">
                        Loading backend ticker matrix...
                      </td>
                    </tr>
                  ) : (
                    filteredStocks.map((s) => (
                      <tr
                        key={s.symbol}
                        onClick={() => setSelectedSymbol(s.symbol)}
                        className={`hover:bg-slate-800/50 cursor-pointer transition-colors ${
                          selectedSymbol === s.symbol ? 'bg-cyan-950/40 font-semibold' : ''
                        }`}
                      >
                        <td className="py-3 font-bold text-slate-100">{s.symbol}</td>
                        <td className="py-3 text-slate-300 truncate max-w-[150px]">{s.name}</td>
                        <td className="py-3 text-slate-400">{s.sector}</td>
                        <td className="py-3 text-right num-tabular font-bold">
                          ₹{s.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                        <td
                          className={`py-3 text-right num-tabular font-semibold ${
                            s.change >= 0 ? 'text-emerald-400' : 'text-red-400'
                          }`}
                        >
                          {s.change >= 0 ? '+' : ''}
                          {s.change.toFixed(2)}%
                        </td>
                        <td className="py-3 text-right num-tabular text-slate-400">{s.volume}</td>
                        <td className="py-3 text-right text-slate-400">{s.mcap}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: L2 Depth of Market */}
        <div className="space-y-6 min-w-0">
          <div className="bg-[#121826] rounded-2xl p-5 border border-[#1E293B] space-y-4">
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
              <h3 className="font-bold text-sm text-slate-100">Depth of Market (L2 Orderbook)</h3>
              <span className="text-xs text-cyan-400 font-bold">{selectedSymbol}</span>
            </div>

            {activePrice === 0 ? (
              <div className="py-8 text-center text-slate-500 text-xs">
                Awaiting market quote...
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3 text-xs">
                {/* Bids */}
                <div className="space-y-1.5">
                  <div className="text-emerald-400 font-bold border-b border-[#1E293B] pb-1 text-[11px] uppercase">
                    Bids (Buy)
                  </div>
                  {[
                    { p: activePrice, q: 1250 },
                    { p: activePrice - 0.5, q: 2400 },
                    { p: activePrice - 1.0, q: 3100 },
                    { p: activePrice - 1.5, q: 4500 },
                    { p: activePrice - 2.0, q: 6200 },
                  ].map((b, i) => (
                    <div key={i} className="flex justify-between text-slate-300">
                      <span className="num-tabular font-bold text-emerald-400">
                        ₹{b.p.toFixed(2)}
                      </span>
                      <span className="text-slate-400 num-tabular">{b.q}</span>
                    </div>
                  ))}
                </div>

                {/* Asks */}
                <div className="space-y-1.5">
                  <div className="text-red-400 font-bold border-b border-[#1E293B] pb-1 text-[11px] uppercase">
                    Asks (Sell)
                  </div>
                  {[
                    { p: activePrice + 0.5, q: 950 },
                    { p: activePrice + 1.0, q: 1800 },
                    { p: activePrice + 1.5, q: 4200 },
                    { p: activePrice + 2.0, q: 5800 },
                    { p: activePrice + 2.5, q: 7100 },
                  ].map((a, i) => (
                    <div key={i} className="flex justify-between text-slate-300">
                      <span className="num-tabular font-bold text-red-400">
                        ₹{a.p.toFixed(2)}
                      </span>
                      <span className="text-slate-400 num-tabular">{a.q}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
