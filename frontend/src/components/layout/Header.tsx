import React, { useState, useEffect } from 'react';
import { Search, Command, Activity, Server, Sun, Moon, Zap, ShieldCheck, Clock } from 'lucide-react';
import { useSettingsStore } from '../../store/useSettingsStore';
import { useSystemHealth } from '../../hooks/useSystemHealth';

interface HeaderProps {
  onOpenCommandPalette: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenCommandPalette }) => {
  const { backendUrl, theme, setTheme } = useSettingsStore();
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

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    if (newTheme === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
  };

  const marketTickers = [
    { symbol: 'NIFTY 50', price: '24,180.50', change: '+0.65%', isUp: true },
    { symbol: 'SENSEX', price: '79,450.20', change: '+0.52%', isUp: true },
    { symbol: 'BANKNIFTY', price: '52,340.10', change: '-0.18%', isUp: false },
    { symbol: 'RELIANCE', price: '₹2,980.00', change: '+1.20%', isUp: true },
    { symbol: 'TCS', price: '₹3,850.10', change: '-0.40%', isUp: false },
    { symbol: 'INFY', price: '₹1,820.00', change: '+0.85%', isUp: true },
    { symbol: 'HDFCBANK', price: '₹1,650.00', change: '+0.30%', isUp: true },
    { symbol: 'TATAMOTORS', price: '₹980.50', change: '+2.10%', isUp: true },
  ];

  return (
    <header className="sticky top-0 z-20 flex flex-col border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md">
      {/* Top Ticker Marquee Bar */}
      <div className="overflow-hidden bg-slate-950 border-b border-slate-800/50 py-1 px-4 text-[11px] font-mono text-slate-400 select-none">
        <div className="flex items-center gap-6 animate-ticker whitespace-nowrap">
          {marketTickers.concat(marketTickers).map((t, idx) => (
            <div key={idx} className="flex items-center gap-1.5 shrink-0">
              <span className="font-semibold text-slate-300">{t.symbol}</span>
              <span className="text-slate-400 num-tabular">{t.price}</span>
              <span className={t.isUp ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'}>
                {t.change}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="flex h-14 items-center justify-between px-6">
        {/* Search Command Trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenCommandPalette}
            className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/90 px-3.5 py-1.5 text-xs text-slate-400 hover:border-slate-700 hover:text-slate-200 transition-all w-72 shadow-inner group"
          >
            <Search className="h-3.5 w-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            <span className="flex-1 text-left">Search tickers, actions (Ctrl+K)...</span>
            <kbd className="flex items-center gap-0.5 rounded-md bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 border border-slate-700/60">
              <Command className="h-3 w-3" />K
            </kbd>
          </button>
        </div>

        {/* Status Badges & Controls */}
        <div className="flex items-center gap-4 text-xs font-mono">
          {/* Realtime Clock */}
          <div className="hidden sm:flex items-center gap-1.5 text-slate-400 rounded-lg bg-slate-900/80 px-3 py-1 border border-slate-800/60">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span className="num-tabular font-medium text-slate-200">{time}</span>
          </div>

          {/* Broker Status */}
          <div className="hidden md:flex items-center gap-1.5 rounded-lg border border-emerald-800/60 bg-emerald-950/40 px-2.5 py-1 text-emerald-300">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>ZERODHA: CONNECTED</span>
          </div>

          {/* Backend Health Status */}
          <div className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/80 px-2.5 py-1">
            <Activity className={`h-3.5 w-3.5 ${isHealthy ? 'text-emerald-400 animate-pulse' : 'text-rose-400'}`} />
            <span className="text-slate-400">API:</span>
            <span className={isHealthy ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
              {isHealthy ? 'ONLINE' : 'UNREACHABLE'}
            </span>
          </div>

          {/* Theme Switcher Button */}
          <button
            onClick={toggleTheme}
            className="rounded-lg border border-slate-800 bg-slate-900 p-1.5 text-slate-400 hover:text-cyan-300 hover:border-slate-700 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          >
            {theme === 'dark' ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-cyan-400" />}
          </button>
        </div>
      </div>
    </header>
  );
};
