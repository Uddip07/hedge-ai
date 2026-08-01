import React, { useState, useEffect } from 'react';
import { Search, Command, Activity, ShieldCheck, Clock } from 'lucide-react';
import { useSystemHealth } from '../../hooks/useSystemHealth';
import { LiveMarketRibbon } from './LiveMarketRibbon';

interface HeaderProps {
  onOpenCommandPalette: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenCommandPalette }) => {
  const { health } = useSystemHealth();
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }) + ' IST'
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health.data?.data?.status === 'healthy';

  return (
    <header className="sticky top-0 z-20 flex flex-col border-b border-[#1E293B] bg-[#090D16]/95 backdrop-blur-md">
      {/* Live Market WebSocket Ribbon */}
      <LiveMarketRibbon />

      {/* Main Header Bar */}
      <div className="flex h-12 items-center justify-between px-4">
        {/* Search Command Trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenCommandPalette}
            className="flex items-center gap-2 rounded-lg border border-[#1E293B] bg-[#121826] px-3 py-1 text-xs text-slate-400 hover:border-slate-700 hover:text-slate-200 transition-all w-64 md:w-80 shadow-inner group"
          >
            <Search className="h-3.5 w-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            <span className="flex-1 text-left truncate">Search tickers, actions (Ctrl+K)...</span>
            <kbd className="hidden sm:flex items-center gap-0.5 rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 border border-slate-700/60">
              <Command className="h-3 w-3" />K
            </kbd>
          </button>
        </div>

        {/* Status Badges & Controls */}
        <div className="flex items-center gap-3 text-xs font-mono">
          {/* Realtime Clock */}
          <div className="hidden sm:flex items-center gap-1.5 text-slate-400 rounded-lg bg-[#121826] px-2.5 py-1 border border-[#1E293B]">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span className="num-tabular font-medium text-slate-200">{time}</span>
          </div>

          {/* Broker Status */}
          <div className="hidden lg:flex items-center gap-1.5 rounded-lg border border-emerald-800/60 bg-emerald-950/40 px-2.5 py-1 text-emerald-300">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>ZERODHA: ONLINE</span>
          </div>

          {/* Backend Health Status */}
          <div className="flex items-center gap-2 rounded-lg border border-[#1E293B] bg-[#121826] px-2.5 py-1">
            <Activity className={`h-3.5 w-3.5 ${isHealthy ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
            <span className="text-slate-400 hidden sm:inline">FASTAPI:</span>
            <span className={isHealthy ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
              {isHealthy ? 'ONLINE' : 'ACTIVE'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
