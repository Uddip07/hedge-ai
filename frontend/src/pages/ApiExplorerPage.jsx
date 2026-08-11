import React, { useState } from 'react';
import {
  Terminal,
  Play,
  Copy,
  Check,
  Clock,
  Trash2,
  Send,
  Code2,
} from 'lucide-react';
import { apiClient } from '../api/client';
import { useSettingsStore } from '../store/useSettingsStore';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { toast } from '../hooks/useToast';

export const ApiExplorerPage = () => {
  const { apiLogs, clearLogs } = useSettingsStore();

  const presets = [
    { label: 'GET /health', method: 'GET', endpoint: '/health', body: '' },
    { label: 'GET /health/detailed', method: 'GET', endpoint: '/health/detailed', body: '' },
    { label: 'GET /version', method: 'GET', endpoint: '/version', body: '' },
    { label: 'GET /market/summary/daily', method: 'GET', endpoint: '/market/summary/daily', body: '' },
    { label: 'GET /market/RELIANCE.NSE', method: 'GET', endpoint: '/market/RELIANCE.NSE', body: '' },
    { label: 'GET /market/RELIANCE.NSE/history', method: 'GET', endpoint: '/market/RELIANCE.NSE/history', body: '' },
    { label: 'GET /api/v1/market-data/stats', method: 'GET', endpoint: '/api/v1/market-data/stats', body: '' },
    { label: 'GET /api/v1/market-data/symbols', method: 'GET', endpoint: '/api/v1/market-data/symbols', body: '' },
    { label: 'GET /company-intelligence/RELIANCE.NSE', method: 'GET', endpoint: '/company-intelligence/RELIANCE.NSE', body: '' },
    {
      label: 'POST /committee/evaluate',
      method: 'POST',
      endpoint: '/committee/evaluate',
      body: JSON.stringify(
        {
          ticker: 'RELIANCE.NSE',
          horizon: 'LONG_TERM',
          style: 'BALANCED',
          user_query: 'Execute comprehensive institutional multi-agent valuation review.',
        },
        null,
        2
      ),
    },
    {
      label: 'POST /api/v1/backtest/run',
      method: 'POST',
      endpoint: '/api/v1/backtest/run',
      body: JSON.stringify(
        {
          strategy_name: 'MOMENTUM_SMA',
          symbol: 'RELIANCE',
          initial_capital: 1000000,
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          parameters: { sma_window: 20 },
        },
        null,
        2
      ),
    },
    { label: 'GET /broker/health', method: 'GET', endpoint: '/broker/health', body: '' },
    { label: 'GET /broker/funds', method: 'GET', endpoint: '/broker/funds', body: '' },
    { label: 'GET /broker/holdings', method: 'GET', endpoint: '/broker/holdings', body: '' },
    { label: 'GET /broker/orders', method: 'GET', endpoint: '/broker/orders', body: '' },
  ];

  const [method, setMethod] = useState('GET');
  const [endpoint, setEndpoint] = useState('/health');
  const [requestBody, setRequestBody] = useState('');
  const [responseResult, setResponseResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSelectPreset = (preset) => {
    setMethod(preset.method);
    setEndpoint(preset.endpoint);
    setRequestBody(preset.body);
  };

  const handleExecute = async (e) => {
    e?.preventDefault();
    setIsLoading(true);
    setResponseResult(null);

    try {
      const options = { method };
      if (method !== 'GET' && requestBody.trim()) {
        options.body = requestBody;
      }
      const res = await apiClient(endpoint, options);
      setResponseResult(res);
      toast.success('Request Executed', `${method} ${endpoint} [${res.status}] in ${res.latencyMs}ms`);
    } catch (err) {
      setResponseResult({
        status: 'ERR',
        latencyMs: 0,
        data: { error: err.message },
      });
      toast.error('Request Failed', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyResponse = () => {
    if (responseResult?.data) {
      navigator.clipboard.writeText(JSON.stringify(responseResult.data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.info('Copied', 'JSON payload copied to clipboard');
    }
  };

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              INTERACTIVE REST API EXPLORER
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              FASTAPI SPEC
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Real-time HTTP request workbench, live payload inspector & latency tracer
          </p>
        </div>
      </div>

      {/* Preset Quick Actions */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-2">
        <span className="text-slate-500 font-bold block text-[11px] uppercase">
          FASTAPI ENDPOINT PRESETS:
        </span>
        <div className="flex flex-wrap gap-1.5">
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectPreset(p)}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                endpoint === p.endpoint && method === p.method
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'bg-slate-900 border border-[#162235] text-slate-400 hover:text-slate-200'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Request Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Panel */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
              <Send className="h-4 w-4 text-cyan-400" />
              <h3 className="font-bold text-slate-100 text-sm">HTTP Request Builder</h3>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value)}
                className="bg-slate-900 border border-[#162235] rounded-lg px-3 py-2 text-cyan-300 font-bold focus:border-cyan-500"
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </select>

              <input
                type="text"
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                placeholder="/health"
                className="flex-1 bg-slate-900 border border-[#162235] rounded-lg px-3 py-2 text-slate-100 font-bold focus:border-cyan-500 text-xs"
              />
            </div>

            {method !== 'GET' && (
              <div className="space-y-1">
                <label className="block text-slate-400 font-semibold">JSON Request Body</label>
                <textarea
                  rows={8}
                  value={requestBody}
                  onChange={(e) => setRequestBody(e.target.value)}
                  placeholder="{}"
                  className="w-full bg-slate-950 border border-[#162235] rounded-lg p-3 text-slate-200 text-xs font-mono focus:border-cyan-500"
                />
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-[#162235] flex justify-end">
            <Button
              type="button"
              onClick={handleExecute}
              isLoading={isLoading}
              leftIcon={<Play className="h-4 w-4" />}
              className="font-bold w-full sm:w-auto"
            >
              Send HTTP Request
            </Button>
          </div>
        </div>

        {/* Response Panel */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
              <div className="flex items-center gap-2">
                <Code2 className="h-4 w-4 text-cyan-400" />
                <h3 className="font-bold text-slate-100 text-sm">Response Payload</h3>
              </div>

              {responseResult && (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 text-slate-400 text-[11px]">
                    <Clock className="h-3 w-3 text-cyan-400" />
                    <span>{responseResult.latencyMs} ms</span>
                  </div>
                  <StatusBadge status={responseResult.status} size="xs" />
                </div>
              )}
            </div>

            <div className="relative">
              <pre className="p-4 rounded-xl bg-slate-950 border border-[#162235] text-slate-200 text-xs font-mono max-h-96 overflow-y-auto overflow-x-auto leading-relaxed">
                {responseResult
                  ? JSON.stringify(responseResult.data, null, 2)
                  : '// Click "Send HTTP Request" to view live JSON response.'}
              </pre>

              {responseResult && (
                <button
                  type="button"
                  onClick={handleCopyResponse}
                  className="absolute right-3 top-3 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white border border-slate-700 transition-colors cursor-pointer"
                  title="Copy JSON"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* HTTP Request Journal / History */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Session HTTP Journal ({apiLogs.length})</h3>
          </div>

          <Button
            variant="outline"
            size="xs"
            onClick={clearLogs}
            leftIcon={<Trash2 className="h-3 w-3" />}
          >
            Clear Journal
          </Button>
        </div>

        {apiLogs.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No API requests recorded yet in this browser session.
          </div>
        ) : (
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {apiLogs.map((log) => (
              <div
                key={log.id}
                onClick={() => {
                  setMethod(log.method);
                  setEndpoint(log.endpoint);
                  if (log.requestBody) setRequestBody(JSON.stringify(log.requestBody, null, 2));
                }}
                className="p-3 rounded-lg bg-slate-900/80 border border-[#162235] hover:border-cyan-500/40 transition-colors flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                      log.method === 'GET'
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                        : log.method === 'POST'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-purple-950 text-purple-300 border border-purple-800'
                    }`}
                  >
                    {log.method}
                  </span>
                  <span className="font-bold text-slate-200 text-xs">{log.endpoint}</span>
                </div>

                <div className="flex items-center gap-4 text-slate-400 text-[11px] num-tabular">
                  <span>{log.latencyMs} ms</span>
                  <StatusBadge status={log.status} size="xs" />
                  <span className="text-slate-500 text-[10px]">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
