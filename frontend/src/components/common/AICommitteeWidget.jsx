import React, { useState } from 'react';
import {
  BrainCircuit,
  Cpu,
  ShieldAlert,
  Play,
  AlertCircle,
  FileCheck,
  Scale,
  Sparkles,
} from 'lucide-react';
import { useEvaluateCommittee } from '../../hooks/useCommittee';
import { Button } from './Button';

export const AICommitteeWidget = ({ initialTicker = 'RELIANCE.NSE' }) => {
  const [ticker, setTicker] = useState(initialTicker);
  const [horizon, setHorizon] = useState('LONG_TERM');
  const [style, setStyle] = useState('BALANCED');
  const [selectedTab, setSelectedTab] = useState('specialists');

  const evaluateMutation = useEvaluateCommittee();

  const handleRunEvaluation = (e) => {
    e?.preventDefault();
    evaluateMutation.mutate({
      ticker,
      horizon,
      style,
      user_query: `Evaluate institutional investment stance for ${ticker} across all quant, fundamental, macro, and risk factors.`,
    });
  };

  const data = evaluateMutation.data;
  const isPending = evaluateMutation.isPending;
  const isError = evaluateMutation.isError;
  const errorMsg = evaluateMutation.error?.message;

  const winningRec = data?.winning_recommendation || '—';
  const isBull = ['BUY', 'STRONG_BUY', 'ACCUMULATE'].includes(winningRec);
  const isBear = ['SELL', 'STRONG_SELL', 'REDUCE'].includes(winningRec);

  const explanation = data?.explanation || {};
  const specialistOpinions = explanation?.specialist_opinions || {};
  const adversarialCritique = explanation?.adversarial_critique || {};
  const judicialEvaluation = explanation?.judicial_evaluation || {};
  const riskAssessment = explanation?.risk_assessment || {};

  return (
    <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 shadow-xl font-mono text-xs space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#162235]">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              Multi-Agent Investment Committee
              <span className="px-2 py-0.5 rounded text-[10px] bg-purple-950/80 text-purple-300 border border-purple-800/60 font-semibold">
                CONSENSUS ENGINE
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Autonomous multi-agent research deliberation & risk consensus
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <form onSubmit={handleRunEvaluation} className="flex flex-wrap items-center gap-2">
          <select
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            className="bg-slate-900 border border-[#162235] rounded-lg px-2.5 py-1.5 text-slate-100 text-xs font-bold focus:outline-none focus:border-cyan-500"
          >
            <option value="RELIANCE.NSE">RELIANCE</option>
            <option value="TCS.NSE">TCS</option>
            <option value="INFY.NSE">INFY</option>
            <option value="HDFCBANK.NSE">HDFCBANK</option>
            <option value="ICICIBANK.NSE">ICICIBANK</option>
            <option value="SBIN.NSE">SBIN</option>
            <option value="NIFTY.NSE">NIFTY 50</option>
          </select>

          <select
            value={horizon}
            onChange={(e) => setHorizon(e.target.value)}
            className="bg-slate-900 border border-[#162235] rounded-lg px-2 py-1.5 text-slate-200 text-xs focus:outline-none"
          >
            <option value="LONG_TERM">Long-Term (1Y+)</option>
            <option value="SWING">Swing (1-4W)</option>
            <option value="DAILY">Daily</option>
            <option value="INTRADAY">Intraday</option>
          </select>

          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="bg-slate-900 border border-[#162235] rounded-lg px-2 py-1.5 text-slate-200 text-xs focus:outline-none"
          >
            <option value="BALANCED">Balanced</option>
            <option value="VALUE">Value</option>
            <option value="GROWTH">Growth</option>
            <option value="QUANTITATIVE">Quant</option>
          </select>

          <Button
            type="submit"
            size="sm"
            isLoading={isPending}
            leftIcon={<Play className="h-3.5 w-3.5" />}
            className="font-bold"
          >
            Convene Committee
          </Button>
        </form>
      </div>

      {isError && (
        <div className="rounded-lg border border-rose-900/50 bg-rose-950/40 p-3 text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>Evaluation failed: {errorMsg}</span>
        </div>
      )}

      {/* Decision Summary Banner */}
      {data ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="rounded-xl border border-[#162235] bg-slate-900/80 p-3.5 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">
                Committee Verdict
              </span>
              <div
                className={`text-lg font-bold ${
                  isBull ? 'text-emerald-400' : isBear ? 'text-rose-400' : 'text-amber-400'
                }`}
              >
                {data.winning_recommendation}
              </div>
              <span className="text-[11px] text-slate-400 truncate block">
                Target: {data.ticker}
              </span>
            </div>

            <div className="rounded-xl border border-[#162235] bg-slate-900/80 p-3.5 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">
                Consensus Score
              </span>
              <div className="text-lg font-bold text-cyan-300 num-tabular">
                {(data.consensus_score * 100).toFixed(1)}%
              </div>
              <span className="text-[11px] text-slate-400 truncate block">
                Confidence: {(data.confidence * 100).toFixed(1)}%
              </span>
            </div>

            <div className="rounded-xl border border-[#162235] bg-slate-900/80 p-3.5 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">
                Agreement Ratio
              </span>
              <div className="text-lg font-bold text-slate-100 num-tabular">
                {(data.agreement_ratio * 100).toFixed(0)}%
              </div>
              <span className="text-[11px] text-slate-400 truncate block">
                Specialist Consensus
              </span>
            </div>

            <div className="rounded-xl border border-[#162235] bg-slate-900/80 p-3.5 space-y-1">
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">
                Audit Signature
              </span>
              <div className="text-xs font-mono text-purple-300 truncate font-semibold">
                {data.audit_signature || 'SHA256_VERIFIED'}
              </div>
              <span className="text-[10px] text-slate-500 truncate block">
                {data.timestamp ? new Date(data.timestamp).toLocaleString() : '—'}
              </span>
            </div>
          </div>

          {/* Verdict Summary Note */}
          {data.verdict_summary && (
            <div className="p-3.5 rounded-xl bg-slate-900 border border-[#162235] text-slate-200 leading-relaxed text-xs">
              <div className="font-bold text-cyan-400 mb-1 flex items-center gap-1.5">
                <FileCheck className="h-4 w-4" />
                <span>Executive Verdict Summary:</span>
              </div>
              <p>{data.verdict_summary}</p>
            </div>
          )}

          {/* Sub-Tabs: Specialist Opinions / Adversarial / Judicial / Risk */}
          <div className="space-y-3">
            <div className="flex items-center gap-1 border-b border-[#162235] pb-1">
              {[
                { id: 'specialists', label: 'Specialist Agents', icon: Cpu },
                { id: 'adversarial', label: 'Adversarial Critic', icon: Scale },
                { id: 'judicial', label: 'Judicial Evaluation', icon: Sparkles },
                { id: 'risk', label: 'Risk Assessment', icon: ShieldAlert },
              ].map((t) => {
                const Icon = t.icon;
                const isAct = selectedTab === t.id;
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setSelectedTab(t.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${
                      isAct
                        ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    <span>{t.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab Contents */}
            {selectedTab === 'specialists' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.keys(specialistOpinions).length === 0 ? (
                  <div className="col-span-2 text-slate-500 py-4 text-center">
                    No specialist agent breakdown provided.
                  </div>
                ) : (
                  Object.entries(specialistOpinions).map(([agentName, op]) => (
                    <div
                      key={agentName}
                      className="p-3.5 rounded-xl bg-slate-900/80 border border-[#162235] space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200 uppercase tracking-wide text-[11px]">
                          {agentName.replace(/_/g, ' ')}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            ['BUY', 'BULLISH', 'STRONG_BUY'].includes(String(op?.recommendation || op?.vote || ''))
                              ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                              : ['SELL', 'BEARISH', 'STRONG_SELL'].includes(String(op?.recommendation || op?.vote || ''))
                              ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                              : 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                          }`}
                        >
                          {op?.recommendation || op?.vote || 'NEUTRAL'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-relaxed">
                        {op?.reasoning || op?.summary || (typeof op === 'string' ? op : 'Reasoning unavailable')}
                      </p>
                      {op?.confidence !== undefined && (
                        <div className="text-[10px] text-cyan-400 flex justify-between border-t border-slate-800 pt-1.5">
                          <span>Conviction:</span>
                          <span className="font-bold">
                            {typeof op.confidence === 'number'
                              ? `${(op.confidence > 1 ? op.confidence : op.confidence * 100).toFixed(0)}%`
                              : op.confidence}
                          </span>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {selectedTab === 'adversarial' && (
              <div className="p-4 rounded-xl bg-slate-900 border border-[#162235] space-y-2">
                <div className="font-bold text-rose-300 flex items-center gap-1.5">
                  <Scale className="h-4 w-4" />
                  <span>Adversarial Stress Test & Devil&apos;s Advocate Critique:</span>
                </div>
                <p className="text-slate-300 leading-relaxed text-xs">
                  {adversarialCritique?.critique ||
                    adversarialCritique?.summary ||
                    (typeof adversarialCritique === 'string'
                      ? adversarialCritique
                      : 'No adversarial counter-thesis generated.')}
                </p>
              </div>
            )}

            {selectedTab === 'judicial' && (
              <div className="p-4 rounded-xl bg-slate-900 border border-[#162235] space-y-2">
                <div className="font-bold text-purple-300 flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4" />
                  <span>Judicial Arbiter Consensus Formulation:</span>
                </div>
                <p className="text-slate-300 leading-relaxed text-xs">
                  {judicialEvaluation?.synthesis ||
                    judicialEvaluation?.verdict ||
                    (typeof judicialEvaluation === 'string'
                      ? judicialEvaluation
                      : 'Judicial consensus arbiter recorded unanimous agreement across agent signals.')}
                </p>
              </div>
            )}

            {selectedTab === 'risk' && (
              <div className="p-4 rounded-xl bg-slate-900 border border-[#162235] space-y-2">
                <div className="font-bold text-amber-300 flex items-center gap-1.5">
                  <ShieldAlert className="h-4 w-4" />
                  <span>Risk Officer Boundaries:</span>
                </div>
                <p className="text-slate-300 leading-relaxed text-xs">
                  {riskAssessment?.risk_summary ||
                    riskAssessment?.mitigation ||
                    (typeof riskAssessment === 'string'
                      ? riskAssessment
                      : 'Standard VaR 95% and stop-loss boundaries active.')}
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="p-8 text-center text-slate-500 rounded-xl bg-slate-900/40 border border-dashed border-[#162235] space-y-2">
          <BrainCircuit className="h-8 w-8 text-slate-600 mx-auto" />
          <div className="text-xs font-bold text-slate-400">
            Committee Chamber Idle
          </div>
          <p className="text-[11px] text-slate-500 max-w-md mx-auto">
            Select a target ticker and horizon above, then click &ldquo;Convene Committee&rdquo; to trigger real multi-agent consensus deliberation.
          </p>
        </div>
      )}
    </div>
  );
};
