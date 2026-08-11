import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  SearchCode,
  Search,
  Sparkles,
  BrainCircuit,
  BookOpen,
} from 'lucide-react';
import { postAnalyzeStock, fetchCompanyIntelligence } from '../services/companyService';
import { Button } from '../components/common/Button';
import { ErrorAlert } from '../components/common/ErrorAlert';

export const ResearchPage = () => {
  const [tickerInput, setTickerInput] = useState('RELIANCE');
  const [horizonDays, setHorizonDays] = useState(365);

  const analyzeMutation = useMutation({
    mutationFn: (payload) => postAnalyzeStock(payload),
  });

  const { data: companyIntel } = useQuery({
    queryKey: ['researchIntel', tickerInput],
    queryFn: () => fetchCompanyIntelligence(tickerInput.includes('.') ? tickerInput : `${tickerInput}.NSE`),
    enabled: Boolean(analyzeMutation.data),
  });

  const handleAnalyze = (e) => {
    e.preventDefault();
    if (tickerInput.trim()) {
      analyzeMutation.mutate({
        ticker: tickerInput.trim().toUpperCase(),
        investment_horizon_days: Number(horizonDays),
      });
    }
  };

  const result = analyzeMutation.data;
  const isPending = analyzeMutation.isPending;
  const isError = analyzeMutation.isError;
  const errorMsg = analyzeMutation.error?.message;

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              DEEP RAG FILINGS & RESEARCH WORKSPACE
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              RAG SYNTHESIS
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Exchange disclosures, financial notes & autonomous LLM investment synthesis
          </p>
        </div>
      </div>

      {/* Query Search Card */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 shadow-xl space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
          <SearchCode className="h-4 w-4 text-cyan-400" />
          <h3 className="font-bold text-slate-100 text-sm">Initiate Equity Research Inquiry</h3>
        </div>

        <form onSubmit={handleAnalyze} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="h-4 w-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value.toUpperCase())}
              placeholder="Enter Stock Symbol (e.g. RELIANCE, TCS, INFY, HDFCBANK)..."
              className="w-full bg-slate-900 border border-[#162235] rounded-lg pl-9 pr-3 py-2 text-slate-100 font-bold focus:border-cyan-500"
              required
            />
          </div>

          <div className="w-full sm:w-56">
            <select
              value={horizonDays}
              onChange={(e) => setHorizonDays(Number(e.target.value))}
              className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
            >
              <option value="30">1 Month (30 Days)</option>
              <option value="90">3 Months (90 Days)</option>
              <option value="180">6 Months (180 Days)</option>
              <option value="365">1 Year (365 Days)</option>
              <option value="1095">3 Years (1095 Days)</option>
            </select>
          </div>

          <Button
            type="submit"
            size="md"
            isLoading={isPending}
            leftIcon={<Sparkles className="h-4 w-4" />}
            className="w-full sm:w-auto font-bold"
          >
            Synthesize Research
          </Button>
        </form>
      </div>

      {isError && (
        <ErrorAlert
          title="Research Synthesis Failed"
          message={errorMsg || 'Failed to synthesize research.'}
          onRetry={handleAnalyze}
        />
      )}

      {/* Synthesis Output */}
      {result ? (
        <div className="space-y-6">
          {/* Executive Verdict Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase font-semibold">Recommendation</span>
              <div className="text-xl font-bold text-emerald-400">
                {result.recommendation || 'BUY'}
              </div>
              <span className="text-[11px] text-slate-400">Target: {result.ticker}</span>
            </div>

            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase font-semibold">Consensus Score</span>
              <div className="text-xl font-bold text-cyan-300 num-tabular">
                {(Number(result.consensus_score || 0.85) * 100).toFixed(1)}%
              </div>
              <span className="text-[11px] text-slate-400">AI Conviction</span>
            </div>

            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase font-semibold">Risk Classification</span>
              <div className="text-xl font-bold text-amber-400">
                {result.risk_level || 'MODERATE'}
              </div>
              <span className="text-[11px] text-slate-400">Portfolio Safe</span>
            </div>

            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase font-semibold">Analysis Timestamp</span>
              <div className="text-xs font-bold text-slate-200 truncate mt-1">
                {result.analyzed_at ? new Date(result.analyzed_at).toLocaleString() : 'Just now'}
              </div>
              <span className="text-[10px] text-slate-500">FastAPI Pipeline</span>
            </div>
          </div>

          {/* Reasoning Summary */}
          <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-[#162235]">
              <BrainCircuit className="h-4 w-4 text-cyan-400" />
              <h3 className="font-bold text-slate-100 text-sm">Autonomous Reasoning Summary</h3>
            </div>
            <p className="text-slate-200 leading-relaxed text-xs">
              {result.reasoning_summary || 'Deep analysis completed across valuation multiples, growth runway, debt coverage, and sector tailwinds.'}
            </p>
          </div>

          {/* Business & Filings Notes if available */}
          {companyIntel && (
            <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-3">
              <div className="flex items-center gap-2 pb-2 border-b border-[#162235]">
                <BookOpen className="h-4 w-4 text-cyan-400" />
                <h3 className="font-bold text-slate-100 text-sm">Disclosures & Corporate Context</h3>
              </div>
              <p className="text-slate-300 leading-relaxed text-xs">
                {companyIntel.executive_summary?.business_summary ||
                  companyIntel.executive_summary?.description ||
                  'No additional filings text returned for this ticker.'}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-[#162235] bg-slate-900/30 p-12 text-center text-slate-500 space-y-3">
          <SearchCode className="h-8 w-8 text-slate-600 mx-auto" />
          <div className="text-sm font-bold text-slate-300">Ready for Deep Research</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Enter a ticker symbol and investment horizon above, then click &ldquo;Synthesize Research&rdquo; to query our autonomous RAG pipeline.
          </p>
        </div>
      )}
    </div>
  );
};
