import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  X,
  ArrowRight,
  LayoutDashboard,
  TrendingUp,
  Building2,
  BrainCircuit,
  Terminal,
  Activity,
  Settings,
  Zap,
  PieChart,
  Newspaper,
  History,
  SearchCode,
  Bookmark,
} from 'lucide-react';

export const CommandPaletteModal = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const commands = [
    { label: 'Executive Trading Dashboard', category: 'Navigation', icon: LayoutDashboard, path: '/' },
    { label: 'Live Indian Markets Matrix', category: 'Navigation', icon: TrendingUp, path: '/markets' },
    { label: 'Portfolio & Risk Management', category: 'Navigation', icon: PieChart, path: '/portfolio' },
    { label: 'Company Intelligence — RELIANCE', category: 'Research', icon: Building2, path: '/company/RELIANCE' },
    { label: 'Company Intelligence — TCS', category: 'Research', icon: Building2, path: '/company/TCS' },
    { label: 'Company Intelligence — INFY', category: 'Research', icon: Building2, path: '/company/INFY' },
    { label: 'Company Intelligence — HDFCBANK', category: 'Research', icon: Building2, path: '/company/HDFCBANK' },
    { label: 'Multi-Agent AI Investment Committee', category: 'AI Intelligence', icon: BrainCircuit, path: '/committee' },
    { label: 'News & Sentiment NLP Intelligence', category: 'Intelligence', icon: Newspaper, path: '/news' },
    { label: 'Quantitative Strategy Backtesting', category: 'Quant Engine', icon: History, path: '/backtesting' },
    { label: 'Deep RAG Filing Discovery', category: 'Research', icon: SearchCode, path: '/research' },
    { label: 'Watchlist & Real-Time Alerts', category: 'Trading', icon: Bookmark, path: '/watchlist' },
    { label: 'Interactive OpenAPI REST Console', category: 'Developer', icon: Terminal, path: '/api-explorer' },
    { label: 'Infrastructure Health & Telemetry', category: 'System', icon: Activity, path: '/system-health' },
    { label: 'Broker Preferences & Settings', category: 'System', icon: Settings, path: '/settings' },
  ];

  const filtered = commands.filter(
    (c) =>
      c.label.toLowerCase().includes(query.toLowerCase()) ||
      c.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-slate-950/80 p-4 pt-24 backdrop-blur-sm">
      <div
        onClick={onClose}
        className="fixed inset-0"
      />

      <div className="relative z-10 w-full max-w-xl rounded-2xl border border-[#162235] bg-[#0d1524] shadow-2xl overflow-hidden font-mono text-xs">
        {/* Input Bar */}
        <div className="flex items-center border-b border-[#162235] px-4 py-3.5 bg-[#090e17]">
          <Search className="h-4 w-4 text-cyan-400 mr-3 shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search commands, pages, tickers (e.g. RELIANCE)..."
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none text-xs font-mono"
            autoFocus
          />
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Command List */}
        <div className="max-h-80 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 font-mono">
              No actions matching &ldquo;{query}&rdquo;
            </div>
          ) : (
            filtered.map((cmd, idx) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    navigate(cmd.path);
                    onClose();
                  }}
                  className="flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-left text-xs font-mono text-slate-300 hover:bg-cyan-950/60 hover:text-cyan-300 border border-transparent hover:border-cyan-800/50 transition-all group cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-slate-800/80 p-1.5 text-slate-400 group-hover:text-cyan-400 group-hover:bg-cyan-900/40">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="font-medium text-slate-200 group-hover:text-cyan-200">
                        {cmd.label}
                      </div>
                      <div className="text-[10px] text-slate-500">{cmd.category}</div>
                    </div>
                  </div>
                  <ArrowRight className="h-3.5 w-3.5 text-slate-600 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
                </button>
              );
            })
          )}
        </div>

        {/* Footer Shortcuts */}
        <div className="flex items-center justify-between border-t border-[#162235] px-4 py-2.5 bg-[#090e17] text-[10px] text-slate-500 font-mono">
          <span className="flex items-center gap-1">
            <Zap className="h-3 w-3 text-cyan-400" /> Instant Terminal Navigator
          </span>
          <span>Use ↑ ↓ to navigate &bull; Esc to close</span>
        </div>
      </div>
    </div>
  );
};
