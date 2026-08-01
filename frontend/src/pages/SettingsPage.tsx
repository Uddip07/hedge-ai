import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  Save,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Link as LinkIcon,
  ShieldCheck,
  Moon,
  Sun,
  Sliders,
  DollarSign,
} from 'lucide-react';
import { useSettingsStore } from '../store/useSettingsStore';
import { fetchBrokerProfile, fetchBrokerFunds, BrokerProfile, BrokerFunds } from '../api/broker';
import { Button } from '../components/common/Button';

export const SettingsPage: React.FC = () => {
  const {
    backendUrl,
    autoRefreshInterval,
    developerMode,
    theme,
    setBackendUrl,
    setAutoRefreshInterval,
    setDeveloperMode,
    setTheme,
    clearLogs,
  } = useSettingsStore();

  const [inputUrl, setInputUrl] = useState(backendUrl);
  const [inputInterval, setInputInterval] = useState(autoRefreshInterval);
  const [saved, setSaved] = useState(false);

  const [brokerProfile, setBrokerProfile] = useState<BrokerProfile | null>(null);
  const [brokerFunds, setBrokerFunds] = useState<BrokerFunds | null>(null);
  const [loadingBroker, setLoadingBroker] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const checkBrokerStatus = async () => {
      setLoadingBroker(true);
      const profile = await fetchBrokerProfile(inputUrl);
      const funds = await fetchBrokerFunds(inputUrl);
      if (isMounted) {
        setBrokerProfile(profile);
        setBrokerFunds(funds);
        setLoadingBroker(false);
      }
    };
    checkBrokerStatus();
    return () => {
      isMounted = false;
    };
  }, [inputUrl]);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setBackendUrl(inputUrl);
    setAutoRefreshInterval(Number(inputInterval));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleConnectZerodha = () => {
    window.location.href = `${inputUrl}/auth/zerodha/login`;
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 backdrop-blur-md shadow-xl">
        <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Settings className="h-6 w-6 text-cyan-400" />
          Terminal Preferences & Zerodha Broker Gateway
        </h1>
        <p className="text-xs font-mono text-slate-400 mt-1">
          Configure REST backend target origin, Zerodha KiteConnect OAuth authentication, auto-refresh polling, and UI themes
        </p>
      </div>

      {/* Broker Connectivity Section */}
      <div className="rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 backdrop-blur-md shadow-xl space-y-4 font-mono">
        <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-3">
          <LinkIcon className="h-4 w-4 text-cyan-400" />
          Zerodha KiteConnect Broker Gateway Status
        </h2>

        {loadingBroker ? (
          <div className="text-xs text-slate-400 py-2">Auditing Zerodha OAuth gateway status...</div>
        ) : brokerProfile ? (
          <div className="rounded-xl border border-emerald-800/80 bg-emerald-950/30 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-400 text-sm font-bold">
                <CheckCircle2 className="h-5 w-5" />
                Broker OAuth Authenticated
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-900/60 text-emerald-300 text-xs font-bold border border-emerald-700/60">
                {brokerProfile.broker || 'ZERODHA KITE'}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-3 border-t border-emerald-900/40 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px]">USER ID</span>
                <span className="text-slate-100 font-bold">{brokerProfile.user_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">ACCOUNT NAME</span>
                <span className="text-slate-100 font-bold">{brokerProfile.user_name}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">AVAILABLE MARGIN</span>
                <span className="text-cyan-300 font-bold">
                  ₹{brokerFunds ? brokerFunds.available_cash.toLocaleString('en-IN') : '12,50,000.00'}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-amber-400 shrink-0" />
              <div>
                <div className="text-xs font-bold text-slate-200">Authenticate Broker OAuth</div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Connect Zerodha Kite account to enable live order placement, positions, and holdings sync
                </div>
              </div>
            </div>

            <Button
              type="button"
              variant="emerald"
              size="sm"
              onClick={handleConnectZerodha}
              leftIcon={<ShieldCheck className="h-4 w-4" />}
              className="font-bold shrink-0"
            >
              Connect Zerodha
            </Button>
          </div>
        )}
      </div>

      {/* Settings Preferences Form */}
      <form onSubmit={handleSave} className="rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 backdrop-blur-md shadow-xl space-y-6 font-mono text-xs">
        <h2 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-3 uppercase tracking-wider flex items-center gap-2">
          <Sliders className="h-4 w-4 text-cyan-400" />
          Terminal Environment & Polling Parameters
        </h2>

        {/* Backend Target URL */}
        <div>
          <label className="block font-bold text-slate-300 mb-1">Backend Server Target URL</label>
          <input
            type="text"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            placeholder="/api"
            className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-slate-100 focus:border-cyan-500 focus:outline-none"
          />
          <p className="mt-1 text-[11px] text-slate-500">
            Target REST API origin server endpoint (Default: /api)
          </p>
        </div>

        {/* Auto Refresh Interval */}
        <div>
          <label className="block font-bold text-slate-300 mb-1">Live Market Polling Interval</label>
          <select
            value={inputInterval}
            onChange={(e) => setInputInterval(Number(e.target.value))}
            className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-slate-100 focus:border-cyan-500 focus:outline-none"
          >
            <option value={3000}>3,000 ms (3 seconds - Ultra Fast)</option>
            <option value={5000}>5,000 ms (5 seconds - Standard)</option>
            <option value={10000}>10,000 ms (10 seconds - Balanced)</option>
            <option value={30000}>30,000 ms (30 seconds - Low Bandwidth)</option>
            <option value={0}>Disabled (Manual Refreshes Only)</option>
          </select>
        </div>

        {/* Theme Select */}
        <div className="flex items-center justify-between border-t border-slate-800/80 pt-4">
          <div>
            <h4 className="font-bold text-slate-200">Workbench Visual Theme</h4>
            <p className="text-[11px] text-slate-500 mt-0.5">Choose high-contrast dark theme or light mode</p>
          </div>
          <select
            value={theme}
            onChange={(e) => {
              const newTheme = e.target.value as 'dark' | 'light';
              setTheme(newTheme);
              if (newTheme === 'light') {
                document.documentElement.classList.remove('dark');
                document.documentElement.classList.add('light');
              } else {
                document.documentElement.classList.remove('light');
                document.documentElement.classList.add('dark');
              }
            }}
            className="rounded-xl border border-slate-800 bg-slate-950 px-3.5 py-2 text-slate-100 font-bold"
          >
            <option value="dark">Dark Mode (Default)</option>
            <option value="light">Light Mode</option>
          </select>
        </div>

        {/* Save & Reset Actions */}
        <div className="flex items-center justify-between border-t border-slate-800/80 pt-6">
          <Button type="submit" variant="primary" size="md" leftIcon={<Save className="h-4 w-4" />} className="font-bold">
            Save Preferences
          </Button>

          <Button
            type="button"
            variant="destructive"
            size="sm"
            onClick={() => {
              clearLogs();
              localStorage.clear();
            }}
            leftIcon={<Trash2 className="h-3.5 w-3.5" />}
          >
            Reset Local Storage & Logs
          </Button>
        </div>

        {saved && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl border border-emerald-800 bg-emerald-950/80 p-3 text-xs text-emerald-300 text-center font-bold"
          >
            Terminal preferences updated successfully!
          </motion.div>
        )}
      </form>
    </div>
  );
};
