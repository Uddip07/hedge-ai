import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Search,
  Layers,
  BarChart2,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import {
  useDailyMarketSummary,
  useSymbolsList,
  useMarketQuote,
  useMarketHistory,
} from '../hooks/useMarketData';
import { FinancialChart } from '../components/common/FinancialChart';
import { Table } from '../components/common/Table';
import { Button } from '../components/common/Button';

export const LiveMarketPage = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NSE');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: dailySummary, refetch: refetchSummary } = useDailyMarketSummary();
  const { data: registeredSymbols = [] } = useSymbolsList();
  const { data: currentQuote, refetch: refetchQuote } = useMarketQuote(selectedSymbol);
  const { data: chartData, isLoading: chartLoading } = useMarketHistory(selectedSymbol);

  const gainers = dailySummary?.top_gainers || [];
  const losers = dailySummary?.top_losers || [];
  const sectorPerf = dailySummary?.sector_performance || {};
  const breadth = dailySummary?.breadth || { advances: 0, declines: 0, unchanged: 0 };

  const filteredSymbols = registeredSymbols.filter((s) => {
    const sym = typeof s === 'string' ? s : s.symbol || '';
    const matchesSearch = sym.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  const quoteInfo = currentQuote?.data;
  const isUp = quoteInfo?.change_percent !== undefined && quoteInfo.change_percent >= 0;

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              LIVE MARKETS & SECTOR INTELLIGENCE
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              NSE/BSE DEPTH
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Real-time market depth, sector momentum matrix, and symbol explorer
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchSummary();
              refetchQuote();
            }}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Refresh Markets
          </Button>
        </div>
      </div>

      {/* Market Breadth & Sentiment Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Market Breadth</span>
          <div className="text-lg font-bold text-slate-100 flex items-center gap-3 num-tabular">
            <span className="text-emerald-400">▲ {breadth.advances}</span>
            <span className="text-rose-400">▼ {breadth.declines}</span>
            <span className="text-slate-400 font-normal text-xs">{breadth.unchanged} Flat</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden flex mt-2">
            <div
              style={{
                width: `${(breadth.advances / (breadth.advances + breadth.declines + 0.001)) * 100}%`,
              }}
              className="bg-emerald-500 h-full"
            />
            <div
              style={{
                width: `${(breadth.declines / (breadth.advances + breadth.declines + 0.001)) * 100}%`,
              }}
              className="bg-rose-500 h-full"
            />
          </div>
        </div>

        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Active Symbol</span>
          <div className="text-lg font-bold text-cyan-300 truncate">
            {selectedSymbol}
          </div>
          <span className="text-[10px] text-slate-500 truncate block">
            {quoteInfo?.company_name || 'NSE/BSE Listed'}
          </span>
        </div>

        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Live Price</span>
          <div className="text-lg font-bold text-slate-100 num-tabular">
            ₹{quoteInfo?.price ? Number(quoteInfo.price).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '—'}
          </div>
          <span
            className={`text-[11px] font-semibold ${
              isUp ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {isUp ? '+' : ''}
            {quoteInfo?.change_percent ? Number(quoteInfo.change_percent).toFixed(2) : 0}%
          </span>
        </div>

        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Market Status</span>
          <div className={`text-lg font-bold flex items-center gap-2 ${quoteInfo?.is_market_open ? 'text-emerald-400' : 'text-slate-400'}`}>
            <span className={`h-2 w-2 rounded-full ${quoteInfo?.is_market_open ? 'bg-emerald-400 animate-pulse' : 'bg-slate-400'}`} />
            <span>{quoteInfo?.market_state || (quoteInfo?.is_market_open ? 'OPEN' : 'CLOSED')}</span>
          </div>
          <span className="text-[10px] text-slate-500">
            Source: {quoteInfo?.source || 'YAHOO'}
          </span>
        </div>
      </div>

      {/* Chart & Live Quote Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <FinancialChart
            data={chartData || []}
            symbol={selectedSymbol}
            quote={quoteInfo}
            isLoading={chartLoading}
            height={380}
          />

          {/* Detailed Quote Stats Grid */}
          <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Day High</span>
              <div className="font-bold text-emerald-400 num-tabular mt-0.5">
                ₹{quoteInfo?.high ? Number(quoteInfo.high).toLocaleString('en-IN') : '—'}
              </div>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Day Low</span>
              <div className="font-bold text-rose-400 num-tabular mt-0.5">
                ₹{quoteInfo?.low ? Number(quoteInfo.low).toLocaleString('en-IN') : '—'}
              </div>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Volume</span>
              <div className="font-bold text-slate-200 num-tabular mt-0.5">
                {quoteInfo?.volume ? Number(quoteInfo.volume).toLocaleString('en-IN') : '—'}
              </div>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Sector</span>
              <div className="font-bold text-cyan-300 truncate mt-0.5">
                {quoteInfo?.sector || 'Equities'}
              </div>
            </div>
          </div>
        </div>

        {/* Registered Symbols Sidebar Explorer */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#162235]">
            <h3 className="font-bold text-slate-200 flex items-center gap-2">
              <Layers className="h-4 w-4 text-cyan-400" />
              Registered Universe
            </h3>
            <span className="text-[10px] text-slate-500">
              {filteredSymbols.length} Symbols
            </span>
          </div>

          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter symbols (e.g. RELIANCE, TCS)..."
              className="w-full bg-slate-900 border border-[#162235] rounded-lg pl-8 pr-3 py-1.5 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex-1 max-h-96 overflow-y-auto space-y-1 pr-1">
            {filteredSymbols.length === 0 ? (
              <div className="p-6 text-center text-slate-500 text-xs">
                No symbols matching &ldquo;{searchQuery}&rdquo;
              </div>
            ) : (
              filteredSymbols.map((item) => {
                const sym = typeof item === 'string' ? item : item.symbol;
                const isSelected = selectedSymbol === sym || selectedSymbol === `${sym}.NSE`;
                return (
                  <button
                    key={sym}
                    type="button"
                    onClick={() => setSelectedSymbol(sym.includes('.') ? sym : `${sym}.NSE`)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-lg text-left transition-colors cursor-pointer ${
                      isSelected
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                        : 'bg-slate-900/60 hover:bg-slate-800 text-slate-300 border border-transparent'
                    }`}
                  >
                    <span className="font-bold">{sym}</span>
                    <span className="text-[10px] text-slate-500 uppercase">
                      {typeof item === 'object' ? item.exchange || 'NSE' : 'NSE'}
                    </span>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Sector Performance Matrix */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-2">
            <BarChart2 className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Sector Performance Matrix</h3>
          </div>
          <span className="text-[10px] text-slate-500">
            Daily Weighted Returns
          </span>
        </div>

        {Object.keys(sectorPerf).length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            Loading sector metrics from backend daily summary...
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {Object.entries(sectorPerf).map(([sectorName, perf]) => {
              const numVal = typeof perf === 'number' ? perf : Number(perf?.change_percent || 0);
              const isSecUp = numVal >= 0;
              return (
                <div
                  key={sectorName}
                  className="p-3 rounded-lg bg-slate-900/80 border border-[#162235] space-y-1"
                >
                  <span className="text-slate-400 text-[10px] uppercase truncate block font-semibold">
                    {sectorName}
                  </span>
                  <div
                    className={`text-sm font-bold num-tabular flex items-center justify-between ${
                      isSecUp ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    <span>
                      {isSecUp ? '+' : ''}
                      {numVal.toFixed(2)}%
                    </span>
                    {isSecUp ? (
                      <ArrowUpRight className="h-3.5 w-3.5" />
                    ) : (
                      <ArrowDownRight className="h-3.5 w-3.5" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Top Gainers & Top Losers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-emerald-400" />
              <h3 className="font-bold text-slate-100">Top Market Gainers (NSE)</h3>
            </div>
            <span className="text-[10px] text-emerald-400 font-bold">▲ BULLISH</span>
          </div>

          <Table
            columns={[
              { key: 'symbol', header: 'Symbol' },
              {
                key: 'price',
                header: 'Price',
                align: 'right',
                accessor: (r) => `₹${Number(r.price || 0).toLocaleString('en-IN')}`,
              },
              {
                key: 'change_percent',
                header: 'Change %',
                align: 'right',
                accessor: (r) => (
                  <span className="text-emerald-400 font-bold">
                    +{Number(r.change_percent || 0).toFixed(2)}%
                  </span>
                ),
              },
            ]}
            data={gainers}
            onRowClick={(r) => setSelectedSymbol(r.symbol?.includes('.') ? r.symbol : `${r.symbol}.NSE`)}
            emptyText="No gainers data returned"
          />
        </div>

        {/* Top Losers */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-rose-400" />
              <h3 className="font-bold text-slate-100">Top Market Losers (NSE)</h3>
            </div>
            <span className="text-[10px] text-rose-400 font-bold">▼ BEARISH</span>
          </div>

          <Table
            columns={[
              { key: 'symbol', header: 'Symbol' },
              {
                key: 'price',
                header: 'Price',
                align: 'right',
                accessor: (r) => `₹${Number(r.price || 0).toLocaleString('en-IN')}`,
              },
              {
                key: 'change_percent',
                header: 'Change %',
                align: 'right',
                accessor: (r) => (
                  <span className="text-rose-400 font-bold">
                    {Number(r.change_percent || 0).toFixed(2)}%
                  </span>
                ),
              },
            ]}
            data={losers}
            onRowClick={(r) => setSelectedSymbol(r.symbol?.includes('.') ? r.symbol : `${r.symbol}.NSE`)}
            emptyText="No losers data returned"
          />
        </div>
      </div>
    </div>
  );
};
