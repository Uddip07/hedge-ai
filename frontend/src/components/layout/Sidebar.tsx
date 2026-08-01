import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Building2,
  BrainCircuit,
  Terminal,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Zap,
  PieChart,
  Newspaper,
  History,
  SearchCode,
  Bookmark,
} from 'lucide-react';
import { motion } from 'framer-motion';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard, badge: 'PRO' },
    { path: '/markets', label: 'Live Markets', icon: TrendingUp },
    { path: '/portfolio', label: 'Portfolio & Risk', icon: PieChart },
    { path: '/company', label: 'Company Intelligence', icon: Building2 },
    { path: '/committee', label: 'AI Committee', icon: BrainCircuit, badge: 'AI' },
    { path: '/news', label: 'News & Sentiment', icon: Newspaper },
    { path: '/backtesting', label: 'Backtesting Engine', icon: History },
    { path: '/research', label: 'Deep RAG Research', icon: SearchCode },
    { path: '/watchlist', label: 'Watchlist & Alerts', icon: Bookmark },
    { path: '/api-explorer', label: 'API Explorer', icon: Terminal },
    { path: '/system-health', label: 'System Health', icon: Activity },
    { path: '/settings', label: 'Broker & Settings', icon: Settings },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 z-30 flex h-screen flex-col border-r border-white/10 bg-[#080A0E] transition-all duration-300 ease-in-out ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-white/10 px-4">
        {!collapsed && (
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 p-2 shadow-lg shadow-cyan-950/80">
              <ShieldCheck className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold tracking-wider text-slate-100 text-sm font-mono">MONEYYYYYY</span>
              <span className="text-[10px] font-mono text-cyan-400 font-semibold tracking-widest">
                AI HEDGE FUND OS
              </span>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 p-2 mx-auto">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
        )}
        <button
          onClick={onToggle}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-white/5 hover:text-slate-200 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1 p-2.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 rounded-xl px-3 py-2 text-xs font-mono transition-all select-none ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-semibold shadow-md shadow-cyan-950/40'
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent'
                } ${collapsed ? 'justify-center px-0' : ''}`
              }
              title={collapsed ? item.label : undefined}
            >
              {({ isActive }) => (
                <>
                  <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  {!collapsed && (
                    <div className="flex flex-1 items-center justify-between">
                      <span className="truncate">{item.label}</span>
                      {item.badge && (
                        <span
                          className={`rounded px-1.5 py-0.5 text-[9px] font-bold ${
                            item.badge === 'AI'
                              ? 'bg-purple-950/80 text-purple-300 border border-purple-800/60'
                              : 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/60'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer System Status */}
      {!collapsed && (
        <div className="border-t border-white/10 p-3.5 text-xs font-mono bg-surface">
          <div className="flex items-center gap-2 text-slate-300">
            <Zap className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
            <span className="text-xs">PostgreSQL Engine v1.0</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
            <span>NSE/BSE Feeds</span>
            <span className="text-emerald-400 font-semibold">99.9% ONLINE</span>
          </div>
        </div>
      )}
    </aside>
  );
};
