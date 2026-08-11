import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  History,
  Play,
  TrendingUp,
  BarChart3,
  Search,
  Layers,
  ShieldCheck,
} from 'lucide-react';
import { executeBacktest, fetchBacktestRun } from '../services/backtestService';
import { StatCard } from '../components/common/StatCard';
import { Table } from '../components/common/Table';
import { Button } from '../components/common/Button';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { toast } from '../hooks/useToast';

export const BacktestingPage = () => {
  const [strategyId, setStrategyId] = useState('MOMENTUM_SMA');
  const [symbol, setSymbol] = useState('RELIANCE');
  const [initialCapital, setInitialCapital] = useState(1000000);
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [smaWindow, setSmaWindow] = useState(20);
  const [lookupRunId, setLookupRunId] = useState('');

  const runMutation = useMutation({
    mutationFn: (payload) => executeBacktest(payload),
    onSuccess: (data) => {
      toast.success('Backtest Completed', `Run ID: ${data?.run_id || 'SUCCESS'}`);
    },
    onError: (err) => {
      toast.error('Backtest Execution Failed', err.message);
    },
  });

  const lookupQuery = useQuery({
    queryKey: ['backtestRun', lookupRunId],
    queryFn: () => fetchBacktestRun(lookupRunId),
    enabled: Boolean(lookupRunId),
  });

  const handleRunBacktest = (e) => {
    e.preventDefault();
    const cleanSym = symbol.trim().toUpperCase().split('.')[0];
    runMutation.mutate({
      strategy_id: strategyId,
      symbols: [cleanSym],
      initial_capital: Number(initialCapital),
      start_date: startDate,
      end_date: endDate,
      parameters: {
        sma_window: Number(smaWindow),
      },
    });
  };

  const handleLookup = (e) => {
    e.preventDefault();
    if (lookupRunId.trim()) {
      lookupQuery.refetch();
    }
  };

  const currentResult = runMutation.data || lookupQuery.data;
  const isPending = runMutation.isPending || lookupQuery.isFetching;
  const isError = runMutation.isError || lookupQuery.isError;
  const errorMsg = runMutation.error?.message || lookupQuery.error?.message;

  const metrics = currentResult?.metrics || currentResult || {};
  const trades = Array.isArray(currentResult?.trades) ? currentResult.trades : [];

  const totalReturn = Number(metrics.total_return_pct || metrics.return_pct || 0);

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              QUANTITATIVE STRATEGY BACKTESTING ENGINE
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              SIMULATION ENGINE
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Historical price replay, slippage modeling & strategy performance metrics
          </p>
        </div>

        {/* Lookup Run ID */}
        <form onSubmit={handleLookup} className="flex items-center gap-2">
          <input
            type="text"
            value={lookupRunId}
            onChange={(e) => setLookupRunId(e.target.value)}
            placeholder="Lookup Run ID..."
            className="bg-slate-900 border border-[#162235] rounded-lg px-3 py-1.5 text-slate-100 text-xs focus:border-cyan-500 w-44"
          />
          <Button type="submit" size="sm" variant="outline" leftIcon={<Search className="h-3.5 w-3.5" />}>
            Fetch Run
          </Button>
        </form>
      </div>

      {/* Simulation Configuration Card */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 shadow-xl space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
          <History className="h-4 w-4 text-cyan-400" />
          <h3 className="font-bold text-slate-100 text-sm">Strategy & Backtest Parameters</h3>
        </div>

        <form onSubmit={handleRunBacktest} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Strategy Algorithm</label>
              <select
                value={strategyId}
                onChange={(e) => setStrategyId(e.target.value)}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
              >
                <option value="MOMENTUM_SMA">Momentum SMA Breakout</option>
                <option value="MA_CROSSOVER">Dual Moving Average Crossover</option>
                <option value="MEAN_REVERSION">Mean Reversion Bollinger</option>
                <option value="RSI_MOMENTUM">RSI Trend Momentum</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Target Instrument</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="RELIANCE"
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Initial Capital (₹)</label>
              <input
                type="number"
                step="10000"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">SMA Window Period</label>
              <input
                type="number"
                min="3"
                max="200"
                value={smaWindow}
                onChange={(e) => setSmaWindow(Number(e.target.value))}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              size="md"
              isLoading={isPending}
              leftIcon={<Play className="h-4 w-4" />}
              className="font-bold text-sm"
            >
              Run Quantitative Simulation
            </Button>
          </div>
        </form>
      </div>

      {isError && (
        <ErrorAlert
          title="Backtest Run Failed"
          message={errorMsg || 'Failed to simulate strategy over historical data.'}
          onRetry={handleRunBacktest}
        />
      )}

      {/* Simulation Performance Metrics */}
      {currentResult ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="FINAL PORTFOLIO VALUE"
              value={
                metrics.final_value
                  ? `₹${Number(metrics.final_value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                  : '₹0.00'
              }
              change={totalReturn}
              changeLabel="Total Return"
              icon={TrendingUp}
              subtext={`Start: ₹${Number(initialCapital).toLocaleString('en-IN')}`}
            />

            <StatCard
              title="SHARPE RATIO"
              value={metrics.sharpe_ratio !== undefined ? Number(metrics.sharpe_ratio).toFixed(2) : '—'}
              icon={BarChart3}
              subtext="Risk-Adjusted Alpha"
            />

            <StatCard
              title="MAX DRAWDOWN"
              value={
                metrics.max_drawdown !== undefined
                  ? `${Number(metrics.max_drawdown).toFixed(2)}%`
                  : '0.00%'
              }
              icon={ShieldCheck}
              subtext="Worst Peak-to-Trough"
            />

            <StatCard
              title="EXECUTED TRADES"
              value={trades.length || metrics.total_trades || 0}
              icon={Layers}
              subtext={`Win Rate: ${metrics.win_rate ? `${Number(metrics.win_rate).toFixed(1)}%` : '—'}`}
            />
          </div>

          {/* Executed Trades Ledger Table */}
          <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
              <div className="flex items-center gap-2">
                <History className="h-4 w-4 text-cyan-400" />
                <h3 className="font-bold text-slate-100 text-sm">Simulated Trades Ledger</h3>
              </div>
              <span className="text-[10px] text-slate-500">{trades.length} Transactions</span>
            </div>

            <Table
              columns={[
                { key: 'date', header: 'Timestamp' },
                { key: 'symbol', header: 'Symbol' },
                {
                  key: 'action',
                  header: 'Action',
                  accessor: (r) => (
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        r.action === 'BUY'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-rose-950 text-rose-300 border border-rose-800'
                      }`}
                    >
                      {r.action}
                    </span>
                  ),
                },
                { key: 'quantity', header: 'Qty', align: 'right' },
                {
                  key: 'price',
                  header: 'Exec Price',
                  align: 'right',
                  accessor: (r) => `₹${Number(r.price || 0).toLocaleString('en-IN')}`,
                },
                {
                  key: 'pnl',
                  header: 'Realized P&L',
                  align: 'right',
                  accessor: (r) => {
                    if (r.pnl === undefined) return '—';
                    const pnl = Number(r.pnl);
                    return (
                      <span className={pnl >= 0 ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                        {pnl >= 0 ? '+' : ''}₹{pnl.toLocaleString('en-IN')}
                      </span>
                    );
                  },
                },
              ]}
              data={trades}
              emptyText="No trades executed during this simulation period."
            />
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-[#162235] bg-slate-900/30 p-12 text-center text-slate-500 space-y-3">
          <History className="h-8 w-8 text-slate-600 mx-auto" />
          <div className="text-sm font-bold text-slate-300">Ready to Simulate Strategy</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Choose an algorithm and time window above, then click &ldquo;Run Quantitative Simulation&rdquo; to test performance against database prices.
          </p>
        </div>
      )}
    </div>
  );
};
