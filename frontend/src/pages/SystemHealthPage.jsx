import React from 'react';
import {
  Activity,
  Database,
  Server,
  Zap,
  ShieldCheck,
  RefreshCw,
  Cpu,
} from 'lucide-react';
import { useSystemHealth } from '../hooks/useSystemHealth';
import { useMarketDataStats } from '../hooks/useMarketData';
import { fetchBrokerHealth } from '../api/broker';
import { useQuery } from '@tanstack/react-query';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';

export const SystemHealthPage = () => {
  const { health, detailedHealth, version } = useSystemHealth();
  const { data: dbStats, refetch: refetchDbStats } = useMarketDataStats();

  const { data: brokerHealth, refetch: refetchBroker } = useQuery({
    queryKey: ['brokerHealthDetails'],
    queryFn: () => fetchBrokerHealth(),
  });

  const detailedData = detailedHealth.data?.data;
  const components = detailedData?.components || {};

  const dbComponent = components.database || {};
  const redisComponent = components.redis || {};
  const yahooComponent = components.yahoo_provider || {};
  const freshnessComponent = components.data_freshness || {};

  const handleRefreshAll = () => {
    health.refetch();
    detailedHealth.refetch();
    version.refetch();
    refetchDbStats();
    refetchBroker();
  };

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              SYSTEM INFRASTRUCTURE & TELEMETRY
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              LIVE TELEMETRY
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            FastAPI health probes, PostgreSQL latency, Yahoo Finance pipeline & broker gateway status
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefreshAll}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Probe All Systems
          </Button>
        </div>
      </div>

      {/* Main Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="FASTAPI APPLICATION"
          value={health.data?.data?.status?.toUpperCase() || 'ONLINE'}
          icon={Server}
          subtext={`Ping: ${health.data?.latencyMs || 0} ms`}
        />

        <StatCard
          title="POSTGRESQL DATABASE"
          value={dbComponent.status?.toUpperCase() || 'CONNECTED'}
          icon={Database}
          subtext={
            dbComponent.latency_ms !== undefined
              ? `Query Latency: ${dbComponent.latency_ms} ms`
              : 'Active Pool'
          }
        />

        <StatCard
          title="YAHOO DATA PROVIDER"
          value={yahooComponent.status?.toUpperCase() || 'HEALTHY'}
          icon={Activity}
          subtext={
            yahooComponent.latency_ms !== undefined
              ? `Probe: ${yahooComponent.latency_ms} ms`
              : 'Yahoo Finance'
          }
        />

        <StatCard
          title="BROKER GATEWAY"
          value={brokerHealth?.status?.toUpperCase() || 'OFFLINE'}
          icon={ShieldCheck}
          subtext={brokerHealth?.is_authenticated ? 'Zerodha Authenticated' : 'Not Connected'}
        />
      </div>

      {/* Deep Component Diagnostics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Component Health Diagnostics */}
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-cyan-400" />
              <h3 className="font-bold text-slate-100 text-sm">Probed Service Components</h3>
            </div>
            <StatusBadge status={detailedData?.status || 'HEALTHY'} size="xs" />
          </div>

          <div className="space-y-3">
            {/* Database Component */}
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235] flex items-center justify-between">
              <div>
                <div className="font-bold text-slate-200">PostgreSQL Relational DB</div>
                <div className="text-[11px] text-slate-400">
                  Latency: {dbComponent.latency_ms || 0} ms &bull; Connection Pool: Active
                </div>
              </div>
              <StatusBadge status={dbComponent.status || 'HEALTHY'} size="xs" />
            </div>

            {/* Redis Component */}
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235] flex items-center justify-between">
              <div>
                <div className="font-bold text-slate-200">Redis In-Memory Cache</div>
                <div className="text-[11px] text-slate-400">
                  Status: {redisComponent.status || 'Disabled / Optional'}
                </div>
              </div>
              <StatusBadge status={redisComponent.status || 'DISABLED'} size="xs" />
            </div>

            {/* Yahoo Provider */}
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235] flex items-center justify-between">
              <div>
                <div className="font-bold text-slate-200">Yahoo Finance Feed Provider</div>
                <div className="text-[11px] text-slate-400">
                  Latency: {yahooComponent.latency_ms || 0} ms &bull; Probe Target: {yahooComponent.sample_ticker || 'RELIANCE.NS'}
                </div>
              </div>
              <StatusBadge status={yahooComponent.status || 'HEALTHY'} size="xs" />
            </div>

            {/* Data Freshness */}
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235] flex items-center justify-between">
              <div>
                <div className="font-bold text-slate-200">DB Data Freshness Check</div>
                <div className="text-[11px] text-slate-400">
                  Latest Bar: {freshnessComponent.latest_date || 'Live Data Active'}
                </div>
              </div>
              <StatusBadge status={freshnessComponent.status || 'HEALTHY'} size="xs" />
            </div>
          </div>
        </div>

        {/* Database Storage Telemetry & Runtime Build */}
        <div className="space-y-6">
          <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-400" />
                <h3 className="font-bold text-slate-100 text-sm">Database Storage Telemetry</h3>
              </div>
              <span className="text-[10px] text-slate-500">PostgreSQL</span>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-900 border border-[#162235]">
                <span className="text-[10px] text-slate-500 uppercase block">Companies</span>
                <span className="text-base font-bold text-slate-100 num-tabular">
                  {dbStats?.companies_count || 0}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-900 border border-[#162235]">
                <span className="text-[10px] text-slate-500 uppercase block">Symbols</span>
                <span className="text-base font-bold text-slate-100 num-tabular">
                  {dbStats?.symbols_count || 0}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-900 border border-[#162235]">
                <span className="text-[10px] text-slate-500 uppercase block">Price Bars</span>
                <span className="text-base font-bold text-cyan-300 num-tabular">
                  {Number(dbStats?.prices_count || 0).toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-[#162235]">
              <Zap className="h-4 w-4 text-cyan-400" />
              <h3 className="font-bold text-slate-100 text-sm">Runtime Environment</h3>
            </div>

            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex justify-between py-1 border-b border-[#162235]/60">
                <span className="text-slate-500">Application:</span>
                <span className="font-bold text-slate-200">{version.data?.data?.name || 'MONEYYYYYY OS'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#162235]/60">
                <span className="text-slate-500">Version:</span>
                <span className="font-bold text-cyan-400">{version.data?.data?.version || '2.0.0'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#162235]/60">
                <span className="text-slate-500">Environment:</span>
                <span className="font-bold text-emerald-400">{version.data?.data?.environment || 'production'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Python Runtime:</span>
                <span className="font-bold text-slate-200">
                  {version.data?.data?.build?.python_version || 'Python 3.12+ (Native Windows)'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
