import React, { useState, useEffect } from 'react';
import { Search, Command, Activity, Clock } from 'lucide-react';
import { useSystemHealth } from '../../hooks/useSystemHealth';
import { LiveMarketRibbon } from './LiveMarketRibbon';

export const Header = ({ onOpenCommandPalette }) => {
  const { health } = useSystemHealth();
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const istString = new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }).format(now);
      setTime(`${istString} IST`);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health.data?.data?.status === 'healthy';

  return (
    <header className="sticky top-0 z-20 flex flex-col border-b border-[#162235] bg-[#06080e]/95 backdrop-blur-md">
      {/* Live Market WebSocket Ribbon */}
      <LiveMarketRibbon />

      {/* Main Header Bar */}
      <div className="flex h-12 items-center justify-between px-4">
        {/* Search Command Trigger */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onOpenCommandPalette}
            className="flex items-center gap-2 rounded-lg border border-[#162235] bg-[#0d1524] px-3 py-1 text-xs text-slate-400 hover:border-cyan-500/40 hover:text-slate-200 transition-all w-64 md:w-80 shadow-inner group cursor-pointer"
          >
            <Search className="h-3.5 w-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            <span className="flex-1 text-left truncate">Search tickers, commands (Ctrl+K)...</span>
            <kbd className="hidden sm:flex items-center gap-0.5 rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 border border-slate-700/60">
              <Command className="h-3 w-3" />K
            </kbd>
          </button>
        </div>

        {/* Status Badges & Controls */}
        <div className="flex items-center gap-3 text-xs font-mono">
          {/* Realtime Clock */}
          <div className="hidden sm:flex items-center gap-1.5 text-slate-400 rounded-lg bg-[#0d1524] px-2.5 py-1 border border-[#162235]">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span className="num-tabular font-medium text-slate-200">{time}</span>
          </div>

          {/* Backend Health Status */}
          <div className="flex items-center gap-2 rounded-lg border border-[#162235] bg-[#0d1524] px-2.5 py-1">
            <Activity className={`h-3.5 w-3.5 ${isHealthy ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-slate-400 hidden sm:inline">FASTAPI:</span>
            <span className={isHealthy ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
              {isHealthy ? 'ONLINE' : 'CONNECTING'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
