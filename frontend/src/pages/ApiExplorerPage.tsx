import React, { useState } from 'react';
import { Terminal, Play, Trash2, Code2, Copy, Check } from 'lucide-react';
import { useSettingsStore } from '../store/useSettingsStore';
import { apiClient } from '../api/client';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';

export const ApiExplorerPage: React.FC = () => {
  const { apiLogs, clearLogs } = useSettingsStore();

  const [selectedEndpoint, setSelectedEndpoint] = useState('/health');
  const [selectedMethod, setSelectedMethod] = useState<'GET' | 'POST'>('GET');
  const [requestPayload, setRequestPayload] = useState('{\n  "ticker": "RELIANCE.NSE"\n}');
  const [isExecuting, setIsExecuting] = useState(false);
  const [manualResult, setManualResult] = useState<unknown>(null);
  const [copiedResponse, setCopiedResponse] = useState(false);

  const endpoints = [
    { method: 'GET', path: '/', category: 'System', summary: 'Root Platform Status & Metadata' },
    { method: 'GET', path: '/health', category: 'System', summary: 'Infrastructure Subsystem Health Check' },
    { method: 'GET', path: '/version', category: 'System', summary: 'Software Release Build Metadata' },
    { method: 'GET', path: '/market/RELIANCE.NSE', category: 'Market Data', summary: 'Fetch Real-Time Quote from Yahoo' },
    { method: 'GET', path: '/company-intelligence/RELIANCE.NSE', category: 'Intelligence', summary: 'Generate End-to-End Company Research Report' },
    { method: 'POST', path: '/analyze', category: 'AI Intelligence', summary: 'Analyze Single Stock Thesis' },
    { method: 'POST', path: '/committee/evaluate', category: 'AI Intelligence', summary: 'Execute Multi-Agent Investment Committee' },
    { method: 'GET', path: '/broker/profile', category: 'Broker Gateway', summary: 'Zerodha Kite Account Profile' },
    { method: 'GET', path: '/broker/funds', category: 'Broker Gateway', summary: 'Zerodha Account Available Funds' },
  ];

  const handleExecuteManual = async () => {
    setIsExecuting(true);
    setManualResult(null);

    try {
      const options: RequestInit = {
        method: selectedMethod,
      };

      if (selectedMethod === 'POST') {
        options.body = requestPayload;
      }

      const res = await apiClient(selectedEndpoint, options);
      setManualResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setManualResult({ error: msg });
    } finally {
      setIsExecuting(false);
    }
  };

  const copyResponseJson = () => {
    if (manualResult) {
      navigator.clipboard.writeText(JSON.stringify(manualResult, null, 2));
      setCopiedResponse(true);
      setTimeout(() => setCopiedResponse(false), 2000);
    }
  };

  return (
    <div className="space-y-6 w-full max-w-full min-w-0 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-2xl border border-[#1E293B] bg-[#121826] p-6 shadow-xl">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Terminal className="h-6 w-6 text-cyan-400" />
            Interactive REST API Console & Debugger
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Institutional API console for manually testing endpoints, inspecting JSON responses, and viewing live HTTP logs
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={clearLogs}
          leftIcon={<Trash2 className="h-3.5 w-3.5 text-red-400" />}
          className="hover:border-red-800 hover:text-red-300"
        >
          Clear Logs
        </Button>
      </div>

      {/* Interactive Request Form */}
      <div className="rounded-2xl border border-[#1E293B] bg-[#121826] p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 border-b border-[#1E293B] pb-3">
          <Code2 className="h-4 w-4 text-cyan-400" />
          Request Builder & Execution Suite
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-slate-400 mb-1 font-semibold">HTTP Method</label>
            <select
              value={selectedMethod}
              onChange={(e) => setSelectedMethod(e.target.value as 'GET' | 'POST')}
              className="w-full rounded-xl border border-[#1E293B] bg-slate-900 px-3.5 py-2 text-slate-100 font-bold focus:border-cyan-500 focus:outline-none"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-slate-400 mb-1 font-semibold">Endpoint Route</label>
            <input
              type="text"
              value={selectedEndpoint}
              onChange={(e) => setSelectedEndpoint(e.target.value)}
              className="w-full rounded-xl border border-[#1E293B] bg-slate-900 px-3.5 py-2 text-slate-100 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div className="flex items-end">
            <Button
              type="button"
              variant="primary"
              size="md"
              isLoading={isExecuting}
              onClick={handleExecuteManual}
              leftIcon={<Play className="h-4 w-4" />}
              className="w-full font-bold uppercase tracking-wider"
            >
              Send Request
            </Button>
          </div>
        </div>

        {selectedMethod === 'POST' && (
          <div>
            <label className="block text-slate-400 mb-1 font-semibold">JSON Request Body</label>
            <textarea
              rows={4}
              value={requestPayload}
              onChange={(e) => setRequestPayload(e.target.value)}
              className="w-full rounded-xl border border-[#1E293B] bg-slate-900 p-3 text-slate-100 focus:border-cyan-500 focus:outline-none"
            />
          </div>
        )}

        {/* Response Body Inspector */}
        {manualResult !== null && (
          <div className="rounded-xl border border-[#1E293B] bg-slate-900 p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-2">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-bold">Response JSON Payload</span>
              </div>
              <button
                onClick={copyResponseJson}
                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 transition-colors"
              >
                {copiedResponse ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copiedResponse ? 'Copied' : 'Copy JSON'}</span>
              </button>
            </div>
            <pre className="text-slate-200 overflow-x-auto max-h-72 text-[11px] leading-relaxed">
              {JSON.stringify(manualResult, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Discovered Endpoints Grid */}
      <div className="rounded-2xl border border-[#1E293B] bg-[#121826] p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 border-b border-[#1E293B] pb-3">
          Discovered OpenAPI Endpoints
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {endpoints.map((ep, idx) => (
            <div
              key={idx}
              onClick={() => {
                setSelectedMethod(ep.method as 'GET' | 'POST');
                setSelectedEndpoint(ep.path);
              }}
              className="flex items-center justify-between rounded-xl border border-[#1E293B] bg-slate-900 p-3.5 hover:border-cyan-800 hover:bg-slate-800/60 transition-all cursor-pointer select-none"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${ep.method === 'GET' ? 'text-emerald-400' : 'text-cyan-400'}`}>
                    {ep.method}
                  </span>
                  <span className="text-slate-200 font-bold">{ep.path}</span>
                </div>
                <div className="text-[11px] text-slate-500 mt-1">{ep.summary}</div>
              </div>
              <Play className="h-3.5 w-3.5 text-slate-600 hover:text-cyan-400 transition-colors" />
            </div>
          ))}
        </div>
      </div>

      {/* Live Request Journal */}
      <div className="rounded-2xl border border-[#1E293B] bg-[#121826] p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 border-b border-[#1E293B] pb-3">
          Live HTTP Request Journal ({apiLogs.length})
        </h3>

        <div className="space-y-2 max-h-80 overflow-y-auto">
          {apiLogs.length === 0 ? (
            <div className="text-slate-500 text-center py-8">No HTTP request logs available.</div>
          ) : (
            apiLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between rounded-xl border border-[#1E293B] bg-slate-900 p-3"
              >
                <div className="flex items-center gap-3">
                  <StatusBadge status={String(log.status)} size="sm" />
                  <span className="font-bold text-slate-300">{log.method}</span>
                  <span className="text-slate-200">{log.endpoint}</span>
                </div>
                <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                  <span>{log.latencyMs} ms</span>
                  <span>{log.responseSizeBytes} B</span>
                  <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
