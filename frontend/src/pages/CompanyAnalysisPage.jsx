import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Building2,
  TrendingUp,
  Search,
  FileText,
  BarChart2,
  BrainCircuit,
  Newspaper,
  Flame,
  Snowflake,
} from 'lucide-react';
import { useCompanyIntelligence } from '../hooks/useCompanyIntelligence';
import { useMarketQuote, useMarketHistory } from '../hooks/useMarketData';
import { FinancialChart } from '../components/common/FinancialChart';
import { Tabs } from '../components/common/Tabs';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';

export const CompanyAnalysisPage = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();

  const [inputTicker, setInputTicker] = useState(symbol || 'RELIANCE');
  const [activeTicker, setActiveTicker] = useState(symbol || 'RELIANCE');
  const [activeTab, setActiveTab] = useState('summary');

  const formattedTicker = activeTicker.includes('.') ? activeTicker : `${activeTicker}.NSE`;

  useEffect(() => {
    if (symbol) {
      setActiveTicker(symbol);
      setInputTicker(symbol);
    }
  }, [symbol]);

  const {
    data: intel,
    isLoading: intelLoading,
    isError: intelError,
    error: intelErrObj,
    refetch: refetchIntel,
  } = useCompanyIntelligence(formattedTicker);

  const { data: quoteData } = useMarketQuote(formattedTicker);
  const { data: chartData, isLoading: chartLoading } = useMarketHistory(formattedTicker);

  const handleSearch = (e) => {
    e.preventDefault();
    if (inputTicker.trim()) {
      const clean = inputTicker.trim().toUpperCase();
      setActiveTicker(clean);
      navigate(`/company/${clean}`);
    }
  };

  const handleSelectPill = (sym) => {
    setInputTicker(sym);
    setActiveTicker(sym);
    navigate(`/company/${sym}`);
  };

  const quickPills = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN'];

  const execSummary = intel?.executive_summary || {};
  const finHighlights = intel?.financial_highlights || {};
  const techAnalysis = intel?.technical_analysis || {};
  const bullCase = Array.isArray(intel?.bull_case) ? intel.bull_case : [];
  const bearCase = Array.isArray(intel?.bear_case) ? intel.bear_case : [];
  const newsItems = Array.isArray(intel?.news_section?.articles) ? intel.news_section.articles : [];

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              COMPANY INTELLIGENCE & MULTI-AGENT REPORT
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              DEEP RESEARCH
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Fundamental valuation, technical indicators, filings & multi-agent thesis formulation
          </p>
        </div>

        {/* Quick Ticker Search */}
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={inputTicker}
              onChange={(e) => setInputTicker(e.target.value)}
              placeholder="Ticker (e.g. RELIANCE)..."
              className="bg-slate-900 border border-[#162235] rounded-lg pl-8 pr-3 py-1.5 text-slate-100 font-bold text-xs focus:border-cyan-500 w-44"
            />
          </div>
          <Button type="submit" size="sm" leftIcon={<Search className="h-3.5 w-3.5" />}>
            Analyze
          </Button>
        </form>
      </div>

      {/* Quick Pick Pills */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-slate-500 font-bold">QUICK ANALYSIS:</span>
        {quickPills.map((sym) => (
          <button
            key={sym}
            type="button"
            onClick={() => handleSelectPill(sym)}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTicker === sym
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'bg-slate-900 border border-[#162235] text-slate-400 hover:text-slate-200'
            }`}
          >
            {sym}
          </button>
        ))}
      </div>

      {/* Hero Company Profile Header */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-slate-100">
                {intel?.company_name || activeTicker}
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                {formattedTicker}
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-0.5">
              {quoteData?.data?.sector || 'NSE Equities'} &bull; {quoteData?.data?.industry || 'Indian Large Cap'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 num-tabular">
          <div>
            <span className="text-slate-500 text-[10px] uppercase block">Current LTP</span>
            <span className="text-lg font-bold text-slate-100">
              ₹{quoteData?.data?.price ? Number(quoteData.data.price).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '—'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 text-[10px] uppercase block">Day Change</span>
            <span
              className={`text-sm font-bold ${
                quoteData?.data?.change_percent !== undefined && quoteData.data.change_percent >= 0
                  ? 'text-emerald-400'
                  : 'text-rose-400'
              }`}
            >
              {quoteData?.data?.change_percent !== undefined && quoteData.data.change_percent >= 0 ? '+' : ''}
              {quoteData?.data?.change_percent !== undefined ? Number(quoteData.data.change_percent).toFixed(2) : 0}%
            </span>
          </div>

          <div>
            <span className="text-slate-500 text-[10px] uppercase block">Intelligence</span>
            <StatusBadge status={intel ? 'VERIFIED' : 'SYNCING'} size="xs" />
          </div>
        </div>
      </div>

      {/* Interactive Chart */}
      <FinancialChart
        data={chartData || []}
        symbol={formattedTicker}
        quote={quoteData?.data}
        isLoading={chartLoading}
        height={340}
      />

      {/* Navigation Tabs */}
      <Tabs
        tabs={[
          { id: 'summary', label: 'Executive Summary', icon: FileText },
          { id: 'financials', label: 'Financials & Valuation', icon: BarChart2 },
          { id: 'technical', label: 'Technical Analysis', icon: TrendingUp },
          { id: 'committee', label: 'Multi-Agent Consensus', icon: BrainCircuit },
          { id: 'news', label: 'News & Events', icon: Newspaper, count: newsItems.length },
        ]}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Contents */}
      {intelLoading ? (
        <LoadingSpinner message={`Running quantitative & fundamental pipeline for ${formattedTicker}...`} />
      ) : intelError ? (
        <ErrorAlert
          title={`Intelligence pipeline error for ${formattedTicker}`}
          message={intelErrObj?.message || 'Failed to fetch company intelligence.'}
          onRetry={() => refetchIntel()}
        />
      ) : intel ? (
        <div className="space-y-6">
          {/* TAB 1: SUMMARY */}
          {activeTab === 'summary' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-3">
                <h3 className="font-bold text-sm text-cyan-300 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Executive Business Profile
                </h3>
                <p className="text-slate-300 leading-relaxed text-xs">
                  {execSummary.business_summary ||
                    execSummary.description ||
                    execSummary.summary ||
                    'Corporate overview compiled from latest financial filings and stock exchanges.'}
                </p>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[#162235] text-slate-400">
                  <div>
                    <span className="text-slate-500">Market Cap:</span>{' '}
                    <span className="text-slate-200 font-bold">
                      {execSummary.market_cap ? `₹${Number(execSummary.market_cap).toLocaleString('en-IN')}` : '—'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500">Exchange:</span>{' '}
                    <span className="text-slate-200 font-bold">NSE / BSE</span>
                  </div>
                </div>
              </div>

              {/* Bull vs Bear Case Cards */}
              <div className="space-y-4">
                <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-4 space-y-2">
                  <div className="font-bold text-emerald-400 flex items-center gap-2">
                    <Flame className="h-4 w-4" />
                    <span>Bull Case Thesis</span>
                  </div>
                  {bullCase.length === 0 ? (
                    <p className="text-slate-400 text-xs">Strong market leadership and solid cash generation capacity.</p>
                  ) : (
                    <ul className="space-y-1.5 text-slate-300 text-xs list-disc list-inside">
                      {bullCase.map((b, i) => (
                        <li key={i} className="leading-relaxed">{b}</li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="rounded-xl border border-rose-900/40 bg-rose-950/20 p-4 space-y-2">
                  <div className="font-bold text-rose-400 flex items-center gap-2">
                    <Snowflake className="h-4 w-4" />
                    <span>Bear Case Risks</span>
                  </div>
                  {bearCase.length === 0 ? (
                    <p className="text-slate-400 text-xs">Macro headwinds and sector valuation sensitivity.</p>
                  ) : (
                    <ul className="space-y-1.5 text-slate-300 text-xs list-disc list-inside">
                      {bearCase.map((b, i) => (
                        <li key={i} className="leading-relaxed">{b}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: FINANCIALS */}
          {activeTab === 'financials' && (
            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <BarChart2 className="h-4 w-4 text-cyan-400" />
                Key Valuation & Financial Statements
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {Object.entries(finHighlights).map(([key, val]) => (
                  <div key={key} className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235]">
                    <span className="text-slate-500 text-[10px] uppercase truncate block">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <div className="text-sm font-bold text-slate-100 num-tabular mt-1">
                      {typeof val === 'number'
                        ? val > 1000000
                          ? `₹${(val / 10000000).toFixed(2)} Cr`
                          : val.toLocaleString('en-IN')
                        : String(val)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: TECHNICAL */}
          {activeTab === 'technical' && (
            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-cyan-400" />
                Quantitative Momentum & Technical Analysis
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {Object.entries(techAnalysis).map(([key, val]) => (
                  <div key={key} className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235]">
                    <span className="text-slate-500 text-[10px] uppercase truncate block">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <div className="text-sm font-bold text-cyan-300 num-tabular mt-1">
                      {typeof val === 'number' ? val.toFixed(2) : String(val)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: COMMITTEE DELIBERATION */}
          {activeTab === 'committee' && (
            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
                <h3 className="font-bold text-sm text-purple-300 flex items-center gap-2">
                  <BrainCircuit className="h-4 w-4" />
                  Specialist Multi-Agent Consensus
                </h3>
                <span className="text-[10px] text-slate-500">Autonomous Reasoning</span>
              </div>

              {intel.agent_opinions ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(intel.agent_opinions).map(([agent, op]) => (
                    <div key={agent} className="p-4 rounded-xl bg-slate-900/80 border border-[#162235] space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200 uppercase">{agent.replace(/_/g, ' ')}</span>
                        <StatusBadge status={op?.recommendation || op?.vote || 'BUY'} size="xs" />
                      </div>
                      <p className="text-slate-300 leading-relaxed text-xs">
                        {op?.reasoning || (typeof op === 'string' ? op : 'Reasoning provided by specialist module.')}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-slate-500">
                  No previous committee deliberation recorded for this ticker. Use the AI Committee page to evaluate.
                </div>
              )}
            </div>
          )}

          {/* TAB 5: NEWS */}
          {activeTab === 'news' && (
            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
                <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                  <Newspaper className="h-4 w-4 text-cyan-400" />
                  Recent Headlines & Corporate Filings
                </h3>
                <span className="text-[10px] text-slate-500">{newsItems.length} Articles</span>
              </div>

              {newsItems.length === 0 ? (
                <div className="p-8 text-center text-slate-500">
                  No verified news articles available for {formattedTicker}.
                </div>
              ) : (
                <div className="space-y-3">
                  {newsItems.map((item, i) => (
                    <div key={i} className="p-3.5 rounded-lg bg-slate-900/80 border border-[#162235] space-y-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-slate-200 text-xs">{item.title || item.headline}</h4>
                        <span className="text-[10px] text-slate-500">{item.source || 'NSE'}</span>
                      </div>
                      <p className="text-slate-400 text-xs">{item.summary || item.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};
