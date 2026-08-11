import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Bookmark,
  Plus,
  Trash2,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Send,
  RefreshCw,
  Eye,
} from 'lucide-react';
import { useMarketOverview } from '../hooks/useMarketData';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchRecentAlerts, dispatchAlert } from '../services/alertService';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { Table } from '../components/common/Table';
import { toast } from '../hooks/useToast';

export const WatchlistPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [watchlist, setWatchlist] = useState([
    'RELIANCE.NSE',
    'TCS.NSE',
    'INFY.NSE',
    'HDFCBANK.NSE',
    'ICICIBANK.NSE',
    'SBIN.NSE',
  ]);
  const [newTicker, setNewTicker] = useState('');

  const [alertForm, setAlertForm] = useState({
    symbol: 'RELIANCE',
    title: 'Price Threshold Crossed',
    message: 'RELIANCE broke 52-week moving resistance on high volume.',
    severity: 'WARNING',
  });

  const { data: quotes = {}, refetch: refetchQuotes } = useMarketOverview();
  const { tickerMap } = useWebSocket();

  const { data: alerts = [], refetch: refetchAlerts } = useQuery({
    queryKey: ['recentAlertsFull'],
    queryFn: () => fetchRecentAlerts(20),
  });

  const alertMutation = useMutation({
    mutationFn: (payload) => dispatchAlert(payload),
    onSuccess: () => {
      toast.success('Alert Dispatched', 'Test alert dispatched to event bus.');
      queryClient.invalidateQueries({ queryKey: ['recentAlertsFull'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardRecentAlerts'] });
    },
    onError: (err) => {
      toast.error('Dispatch Failed', err.message);
    },
  });

  const handleAddTicker = (e) => {
    e.preventDefault();
    if (newTicker.trim()) {
      const formatted = newTicker.trim().toUpperCase().includes('.')
        ? newTicker.trim().toUpperCase()
        : `${newTicker.trim().toUpperCase()}.NSE`;
      if (!watchlist.includes(formatted)) {
        setWatchlist([...watchlist, formatted]);
        toast.success('Watchlist Updated', `Added ${formatted}`);
        setNewTicker('');
      }
    }
  };

  const handleRemoveTicker = (sym) => {
    setWatchlist(watchlist.filter((s) => s !== sym));
    toast.info('Watchlist Updated', `Removed ${sym}`);
  };

  const handleDispatchAlert = (e) => {
    e.preventDefault();
    alertMutation.mutate(alertForm);
  };

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              PORTFOLIO WATCHLIST & REAL-TIME ALERTS
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              TELEMETRY & TRIGGERS
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Custom equity monitor, live price tickers & platform alert dispatcher
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchQuotes();
              refetchAlerts();
            }}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Refresh All
          </Button>
        </div>
      </div>

      {/* Add Ticker Bar */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-slate-300 font-bold">
          <Bookmark className="h-4 w-4 text-cyan-400" />
          <span>Active Watchlist Instruments:</span>
        </div>

        <form onSubmit={handleAddTicker} className="flex items-center gap-2 w-full sm:w-auto">
          <input
            type="text"
            value={newTicker}
            onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
            placeholder="Add Ticker (e.g. TATAMOTORS)..."
            className="bg-slate-900 border border-[#162235] rounded-lg px-3 py-1.5 text-slate-100 font-bold text-xs focus:border-cyan-500 w-52"
          />
          <Button type="submit" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
            Add
          </Button>
        </form>
      </div>

      {/* Watchlist Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {watchlist.map((sym) => {
          const wsItem = tickerMap[sym] || tickerMap[sym.split('.')[0]];
          const restQuote = quotes[sym];
          const price = wsItem?.price ?? restQuote?.price ?? null;
          const changePct = wsItem?.change_percent ?? restQuote?.change_percent ?? 0;
          const isUp = changePct >= 0;

          return (
            <div
              key={sym}
              className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex flex-col justify-between space-y-3 hover:border-[#1f3350] transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-sm text-slate-100">{sym}</div>
                  <div className="text-[10px] text-slate-500">
                    {restQuote?.company_name || 'NSE Equities'}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveTicker(sym)}
                  className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-950/40 transition-colors cursor-pointer"
                  title="Remove ticker"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>

              <div className="flex items-end justify-between pt-2 border-t border-[#162235] num-tabular">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">LTP</span>
                  <div className="text-lg font-bold text-slate-100">
                    {price !== null ? `₹${Number(price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                  </div>
                </div>

                <div className="text-right">
                  <div
                    className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded text-[11px] font-bold ${
                      isUp ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'
                    }`}
                  >
                    {isUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    <span>{isUp ? '+' : ''}{Number(changePct).toFixed(2)}%</span>
                  </div>
                </div>
              </div>

              <Button
                variant="outline"
                size="xs"
                onClick={() => navigate(`/company/${sym.split('.')[0]}`)}
                leftIcon={<Eye className="h-3 w-3" />}
                className="w-full mt-1"
              >
                Inspect Intelligence
              </Button>
            </div>
          );
        })}
      </div>

      {/* Bottom Grid: Alerts Ledger & Dispatcher Tool */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts Feed Table */}
        <div className="lg:col-span-2 rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <h3 className="font-bold text-slate-100 text-sm">Platform Alert History</h3>
            </div>
            <span className="text-[10px] text-slate-500">{alerts.length} Events Logged</span>
          </div>

          <Table
            columns={[
              {
                key: 'severity',
                header: 'Severity',
                accessor: (r) => <StatusBadge status={r.severity || 'INFO'} size="xs" />,
              },
              { key: 'symbol', header: 'Symbol' },
              { key: 'title', header: 'Event Title' },
              {
                key: 'created_at',
                header: 'Timestamp',
                align: 'right',
                accessor: (r) =>
                  r.created_at
                    ? new Intl.DateTimeFormat('en-IN', {
                        timeZone: 'Asia/Kolkata',
                        hour12: false,
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                      }).format(new Date(r.created_at)) + ' IST'
                    : 'Recent',
              },
            ]}
            data={alerts}
            emptyText="No alerts recorded."
          />
        </div>

        {/* Test Alert Dispatcher Form */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
            <Send className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Dispatch Platform Alert</h3>
          </div>

          <form onSubmit={handleDispatchAlert} className="space-y-3">
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Target Symbol</label>
              <input
                type="text"
                value={alertForm.symbol}
                onChange={(e) => setAlertForm({ ...alertForm, symbol: e.target.value.toUpperCase() })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Severity Level</label>
              <select
                value={alertForm.severity}
                onChange={(e) => setAlertForm({ ...alertForm, severity: e.target.value })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
              >
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Alert Title</label>
              <input
                type="text"
                value={alertForm.title}
                onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Message Description</label>
              <textarea
                rows={3}
                value={alertForm.message}
                onChange={(e) => setAlertForm({ ...alertForm, message: e.target.value })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-200 text-xs focus:border-cyan-500"
                required
              />
            </div>

            <Button
              type="submit"
              size="sm"
              isLoading={alertMutation.isPending}
              leftIcon={<Send className="h-3.5 w-3.5" />}
              className="w-full font-bold"
            >
              Dispatch Event
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};
