import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  Activity,
  Database,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Wallet,
} from 'lucide-react';
import {
  useMarketOverview,
  useDailyMarketSummary,
  useMarketDataStats,
  useMarketHistory,
  useMarketQuote,
} from '../hooks/useMarketData';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchBrokerFunds, fetchBrokerHealth } from '../api/broker';
import { fetchRecentAlerts } from '../services/alertService';
import { StatCard } from '../components/common/StatCard';
import { FinancialChart } from '../components/common/FinancialChart';
import { AICommitteeWidget } from '../components/common/AICommitteeWidget';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';

export const DashboardPage = () => {
  const [selectedChartSymbol, setSelectedChartSymbol] = useState('RELIANCE.NSE');

  // Real backend queries
  const { data: quotes, refetch: refetchQuotes } = useMarketOverview();
  const { data: dailySummary } = useDailyMarketSummary();
  const { data: dbStats } = useMarketDataStats();
  const { data: chartHistory, isLoading: chartLoading } = useMarketHistory(selectedChartSymbol);
  const { data: selectedQuoteData } = useMarketQuote(selectedChartSymbol);

  const { data: brokerFunds } = useQuery({
    queryKey: ['brokerFunds'],
    queryFn: () => fetchBrokerFunds(),
  });

  const { data: brokerHealth } = useQuery({
    queryKey: ['brokerHealth'],
    queryFn: () => fetchBrokerHealth(),
  });

  const { data: recentAlerts } = useQuery({
    queryKey: ['dashboardRecentAlerts'],
    queryFn: () => fetchRecentAlerts(5),
  });

  const { tickerList, tickerMap, status: wsStatus } = useWebSocket();

  const niftyQuote = tickerMap?.['NIFTY.NSE'] || tickerMap?.['NIFTY'] || quotes?.['NIFTY.NSE'];
  const bankNiftyQuote =
    tickerMap?.['BANKNIFTY.NSE'] || tickerMap?.['BANKNIFTY'] || quotes?.['BANKNIFTY.NSE'];
  const sensexQuote =
    tickerMap?.['SENSEX.BSE'] || tickerMap?.['SENSEX'] || quotes?.['SENSEX.BSE'];

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Top Banner / Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              QUANTITATIVE COMMAND CENTER
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              TERMINAL V2
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Real-time market streaming, multi-agent AI committee deliberation & execution engine
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetchQuotes()}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Refresh Telemetry
          </Button>
        </div>
      </div>

      {/* Benchmark Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="NIFTY 50 (NSE)"
          value={
            niftyQuote?.price !== undefined
              ? `₹${Number(niftyQuote.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
              : '—'
          }
          change={niftyQuote?.change_percent}
          changeLabel="Daily Change"
          icon={TrendingUp}
          subtext={niftyQuote ? `${niftyQuote.sector || 'Broad Index'}` : 'Connecting...'}
        />

        <StatCard
          title="BANK NIFTY (NSE)"
          value={
            bankNiftyQuote?.price !== undefined
              ? `₹${Number(bankNiftyQuote.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
              : '—'
          }
          change={bankNiftyQuote?.change_percent}
          changeLabel="Daily Change"
          icon={TrendingUp}
          subtext={bankNiftyQuote ? `${bankNiftyQuote.sector || 'Banking'}` : 'Connecting...'}
        />

        <StatCard
          title="SENSEX (BSE)"
          value={
            sensexQuote?.price !== undefined
              ? `₹${Number(sensexQuote.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
              : '—'
          }
          change={sensexQuote?.change_percent}
          changeLabel="Daily Change"
          icon={TrendingUp}
          subtext={sensexQuote ? 'BSE Bench' : 'Connecting...'}
        />

        <StatCard
          title="BROKER LIQUIDITY"
          value={
            brokerFunds?.available_cash !== undefined
              ? `₹${Number(brokerFunds.available_cash).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
              : '—'
          }
          icon={Wallet}
          subtext={
            brokerHealth?.is_authenticated
              ? `Margin: ₹${Number(brokerFunds?.net || 0).toLocaleString('en-IN')}`
              : 'Zerodha Disconnected'
          }
        />
      </div>

      {/* Database & Market Breadth Telemetry Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* DB Telemetry */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Database className="h-4 w-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400">PostgreSQL Market DB</div>
              <div className="text-sm font-bold text-slate-100 num-tabular">
                {dbStats?.companies_count || 0} Companies &bull; {dbStats?.symbols_count || 0} Symbols
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-slate-500">Total Price Bars</div>
            <div className="text-xs font-bold text-cyan-300 num-tabular">
              {Number(dbStats?.prices_count || 0).toLocaleString('en-IN')}
            </div>
          </div>
        </div>

        {/* Market Breadth */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Activity className="h-4 w-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400">Market Breadth (NSE)</div>
              <div className="text-sm font-bold text-slate-100 flex items-center gap-2 num-tabular">
                <span className="text-emerald-400">+{dailySummary?.breadth?.advances || 0} Adv</span>
                <span className="text-rose-400">-{dailySummary?.breadth?.declines || 0} Dec</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-slate-500">Unchanged</div>
            <div className="text-xs font-bold text-slate-400 num-tabular">
              {dailySummary?.breadth?.unchanged || 0}
            </div>
          </div>
        </div>

        {/* System & Stream Health */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400">Stream Connection</div>
              <div className="text-sm font-bold text-slate-100">
                WebSocket: {wsStatus}
              </div>
            </div>
          </div>
          <StatusBadge status={wsStatus} size="sm" />
        </div>
      </div>

      {/* Chart Canvas with Symbol Selector */}
      <div className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-bold">ACTIVE ASSET:</span>
            <div className="flex items-center gap-1.5 flex-wrap">
              {['RELIANCE.NSE', 'TCS.NSE', 'INFY.NSE', 'HDFCBANK.NSE', 'ICICIBANK.NSE', 'SBIN.NSE'].map(
                (sym) => (
                  <button
                    key={sym}
                    type="button"
                    onClick={() => setSelectedChartSymbol(sym)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      selectedChartSymbol === sym
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                        : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-[#162235]'
                    }`}
                  >
                    {sym.split('.')[0]}
                  </button>
                )
              )}
            </div>
          </div>

          <div className="text-xs text-slate-400 flex items-center gap-2">
            <span>Current:</span>
            <span className="font-bold text-slate-100">
              {selectedQuoteData?.data?.price !== undefined
                ? `₹${Number(selectedQuoteData.data.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                : '—'}
            </span>
          </div>
        </div>

        <FinancialChart
          data={chartHistory || []}
          symbol={selectedChartSymbol}
          quote={selectedQuoteData?.data}
          isLoading={chartLoading}
          height={380}
        />
      </div>

      {/* AI Committee Evaluation Chamber */}
      <AICommitteeWidget initialTicker={selectedChartSymbol} />

      {/* Bottom Grid: Live Matrix & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live Market Matrix */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-cyan-400" />
              <h3 className="font-bold text-slate-100">Live Streaming Matrix</h3>
            </div>
            <span className="text-[10px] text-slate-500">
              {tickerList.length} Active Feeds
            </span>
          </div>

          {tickerList.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              Waiting for live ticks from WebSocket stream...
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-72 overflow-y-auto">
              {tickerList.map((item) => {
                const isUp = item.change >= 0;
                return (
                  <div
                    key={item.ticker}
                    className="p-3 rounded-lg bg-slate-900/80 border border-[#162235] flex items-center justify-between"
                  >
                    <div>
                      <div className="font-bold text-slate-200">{item.name || item.ticker}</div>
                      <div className="text-[10px] text-slate-500">{item.ticker}</div>
                    </div>
                    <div className="text-right num-tabular">
                      <div className="font-bold text-slate-100">
                        {typeof item.price === 'number' && item.price > 0
                          ? `₹${item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                          : '—'}
                      </div>
                      <div className={`text-[11px] font-semibold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {isUp ? '+' : ''}
                        {typeof item.change_percent === 'number' ? item.change_percent.toFixed(2) : item.change_percent}%
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Platform Alerts */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <h3 className="font-bold text-slate-100">Platform Alerts & Signals</h3>
            </div>
            <span className="text-[10px] text-slate-500">Live Telemetry</span>
          </div>

          {!recentAlerts || recentAlerts.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              No recent alert events logged. System nominal.
            </div>
          ) : (
            <div className="space-y-2.5 max-h-72 overflow-y-auto">
              {recentAlerts.map((alert, i) => (
                <div
                  key={alert.id || i}
                  className="p-3 rounded-lg bg-slate-900/80 border border-[#162235] space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-200 text-[11px]">
                      {alert.symbol || alert.title || 'SYSTEM EVENT'}
                    </span>
                    <StatusBadge status={alert.severity || 'INFO'} size="xs" />
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {alert.message || alert.description || JSON.stringify(alert)}
                  </p>
                  <div className="text-[10px] text-slate-500 flex justify-between pt-1">
                    <span>Source: {alert.source || 'Engine'}</span>
                    <span>
                      {alert.created_at
                        ? new Intl.DateTimeFormat('en-IN', {
                            timeZone: 'Asia/Kolkata',
                            hour12: false,
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                          }).format(new Date(alert.created_at)) + ' IST'
                        : 'Recent'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
