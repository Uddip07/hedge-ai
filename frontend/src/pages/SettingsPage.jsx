import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ShieldCheck,
  Server,
  RefreshCw,
  ExternalLink,
  Trash2,
  Database,
  Sliders,
} from 'lucide-react';
import { useSettingsStore } from '../store/useSettingsStore';
import { fetchBrokerHealth, fetchBrokerProfile } from '../api/broker';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { toast } from '../hooks/useToast';

export const SettingsPage = () => {
  const queryClient = useQueryClient();
  const {
    backendUrl,
    setBackendUrl,
    autoRefreshInterval,
    setAutoRefreshInterval,
    developerMode,
    setDeveloperMode,
    clearLogs,
  } = useSettingsStore();

  const [inputUrl, setInputUrl] = useState(backendUrl);

  const { data: brokerHealth, refetch: refetchBroker } = useQuery({
    queryKey: ['settingsBrokerHealth'],
    queryFn: () => fetchBrokerHealth(),
  });

  const { data: brokerProfile } = useQuery({
    queryKey: ['settingsBrokerProfile'],
    queryFn: () => fetchBrokerProfile(),
    enabled: Boolean(brokerHealth?.is_authenticated),
  });

  const handleSaveUrl = (e) => {
    e.preventDefault();
    setBackendUrl(inputUrl.trim());
    toast.success('Settings Saved', 'Backend API Base URL updated.');
  };

  const handleClearCache = () => {
    queryClient.clear();
    clearLogs();
    toast.info('Cache Cleared', 'Client data store and API logs wiped.');
  };

  const isBrokerAuth = Boolean(brokerHealth?.is_authenticated);

  return (
    <div className="space-y-6 pb-12 font-mono text-xs max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              TERMINAL PREFERENCES & BROKER CONFIG
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              CONFIG
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            FastAPI connection settings, Zerodha Kite OAuth gateway & client cache
          </p>
        </div>
      </div>

      {/* Backend API Configuration */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 shadow-xl">
        <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
          <Server className="h-4 w-4 text-cyan-400" />
          <h3 className="font-bold text-slate-100 text-sm">FastAPI Backend Connection</h3>
        </div>

        <form onSubmit={handleSaveUrl} className="space-y-3">
          <div>
            <label className="block text-slate-400 font-semibold mb-1">
              Backend API Base URL
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inputUrl}
                onChange={(e) => setInputUrl(e.target.value)}
                placeholder="/api or http://localhost:8000"
                className="flex-1 bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
              <Button type="submit" size="sm" className="font-bold">
                Update URL
              </Button>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Default &ldquo;/api&rdquo; routes requests through Vite dev reverse proxy to port 8000.
            </p>
          </div>
        </form>
      </div>

      {/* Zerodha KiteConnect OAuth Integration */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Zerodha KiteConnect Broker Integration</h3>
          </div>
          <StatusBadge status={isBrokerAuth ? 'CONNECTED' : 'DISCONNECTED'} size="xs" />
        </div>

        <div className="space-y-3">
          <div className="p-4 rounded-xl bg-slate-900 border border-[#162235] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="font-bold text-slate-200 text-xs">
                {isBrokerAuth ? `Connected as ${brokerProfile?.user_name || 'Zerodha User'}` : 'Zerodha Account Disconnected'}
              </div>
              <div className="text-[11px] text-slate-400">
                {isBrokerAuth
                  ? `User ID: ${brokerProfile?.user_id || 'Active'} &bull; Broker: Zerodha`
                  : 'Click below to initiate Kite OAuth login redirect to authorize live trading.'}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <a
                href="/api/auth/zerodha/login"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-colors shadow-md shadow-cyan-950/60"
              >
                <span>{isBrokerAuth ? 'Re-authenticate Zerodha' : 'Connect Zerodha Account'}</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetchBroker()}
                leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
              >
                Check
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Auto-Refresh Polling & Telemetry Preferences */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 shadow-xl">
        <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
          <Sliders className="h-4 w-4 text-cyan-400" />
          <h3 className="font-bold text-slate-100 text-sm">Telemetry Polling Interval</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-slate-400 font-semibold mb-1">
              Auto-Refresh Cadence
            </label>
            <select
              value={autoRefreshInterval}
              onChange={(e) => setAutoRefreshInterval(Number(e.target.value))}
              className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500 font-bold"
            >
              <option value="1000">1 Second (Ultra-Fast)</option>
              <option value="2500">2.5 Seconds (Fast)</option>
              <option value="5000">5 Seconds (Recommended)</option>
              <option value="10000">10 Seconds (Relaxed)</option>
              <option value="30000">30 Seconds</option>
              <option value="0">Manual Refresh Only</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 font-semibold mb-1">Developer Mode</label>
            <button
              type="button"
              onClick={() => setDeveloperMode(!developerMode)}
              className={`w-full p-2 rounded-lg font-bold border transition-colors flex items-center justify-between cursor-pointer ${
                developerMode
                  ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                  : 'bg-slate-900 text-slate-400 border-[#162235]'
              }`}
            >
              <span>API Explorer & Diagnostic Telemetry</span>
              <span>{developerMode ? 'ENABLED' : 'DISABLED'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Cache & Maintenance */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Client Store & Cache Reset</h3>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <p className="text-slate-400 text-xs">
            Flush in-memory React Query cache and clear API session request logs.
          </p>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleClearCache}
            leftIcon={<Trash2 className="h-3.5 w-3.5" />}
          >
            Purge Client Cache
          </Button>
        </div>
      </div>
    </div>
  );
};
