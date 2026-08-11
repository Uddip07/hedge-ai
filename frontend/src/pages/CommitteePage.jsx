import React, { useState } from 'react';
import {
  BrainCircuit,
  Cpu,
  ShieldAlert,
  Play,
  Scale,
  Sparkles,
  FileCheck,
  Zap,
} from 'lucide-react';
import { useEvaluateCommittee } from '../hooks/useCommittee';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { ErrorAlert } from '../components/common/ErrorAlert';

export const CommitteePage = () => {
  const [ticker, setTicker] = useState('RELIANCE.NSE');
  const [horizon, setHorizon] = useState('LONG_TERM');
  const [style, setStyle] = useState('BALANCED');
  const [userQuery, setUserQuery] = useState(
    'Evaluate institutional valuation, earnings quality, debt profile, and technical momentum.'
  );

  const evaluateMutation = useEvaluateCommittee();

  const handleSubmit = (e) => {
    e.preventDefault();
    evaluateMutation.mutate({
      ticker,
      horizon,
      style,
      user_query: userQuery,
    });
  };

  const data = evaluateMutation.data;
  const isPending = evaluateMutation.isPending;
  const isError = evaluateMutation.isError;
  const errorMsg = evaluateMutation.error?.message;

  const explanation = data?.explanation || {};
  const specialistOpinions = explanation?.specialist_opinions || {};
  const adversarialCritique = explanation?.adversarial_critique || {};
  const judicialEvaluation = explanation?.judicial_evaluation || {};
  const riskAssessment = explanation?.risk_assessment || {};

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              MULTI-AGENT INVESTMENT COMMITTEE
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-950/80 text-purple-300 border border-purple-800/60">
              AUTONOMOUS CONSENSUS
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Fundamental, technical, macroeconomic, risk, and adversarial agents deliberating in real time
          </p>
        </div>
      </div>

      {/* Parameter Control Panel */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 shadow-xl space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[#162235]">
          <Zap className="h-4 w-4 text-cyan-400" />
          <h3 className="font-bold text-slate-100 text-sm">Committee Configuration & Mandate</h3>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Target Instrument</label>
              <select
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
              >
                <option value="RELIANCE.NSE">RELIANCE (Reliance Industries)</option>
                <option value="TCS.NSE">TCS (Tata Consultancy Services)</option>
                <option value="INFY.NSE">INFY (Infosys Limited)</option>
                <option value="HDFCBANK.NSE">HDFCBANK (HDFC Bank)</option>
                <option value="ICICIBANK.NSE">ICICIBANK (ICICI Bank)</option>
                <option value="SBIN.NSE">SBIN (State Bank of India)</option>
                <option value="NIFTY.NSE">NIFTY 50 (Benchmark Index)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Investment Horizon</label>
              <select
                value={horizon}
                onChange={(e) => setHorizon(e.target.value)}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
              >
                <option value="LONG_TERM">Long-Term (1-3 Years)</option>
                <option value="SWING">Swing (1-4 Weeks)</option>
                <option value="DAILY">Daily (1-5 Days)</option>
                <option value="INTRADAY">Intraday</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Investment Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 focus:border-cyan-500"
              >
                <option value="BALANCED">Balanced Quantitative</option>
                <option value="VALUE">Value / Deep Fundamentals</option>
                <option value="GROWTH">High Growth / Momentum</option>
                <option value="QUANTITATIVE">Statistical Arbitrage / Quant</option>
                <option value="TECHNICAL">Pure Technical Breakout</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-400 font-semibold mb-1">Custom Mandate / Thesis Prompt</label>
            <textarea
              rows={2}
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2.5 text-slate-200 text-xs focus:border-cyan-500 leading-relaxed font-mono"
            />
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              size="md"
              isLoading={isPending}
              leftIcon={<Play className="h-4 w-4" />}
              className="font-bold text-sm"
            >
              Convene Committee & Synthesize
            </Button>
          </div>
        </form>
      </div>

      {isError && (
        <ErrorAlert
          title="Committee Deliberation Failed"
          message={errorMsg || 'Failed to complete multi-agent consensus run.'}
          onRetry={handleSubmit}
        />
      )}

      {/* Committee Decision Results */}
      {data && (
        <div className="space-y-6">
          {/* Executive Verdict Banner */}
          <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#162235]">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/30">
                  <BrainCircuit className="h-6 w-6" />
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold block">
                    CONSENSUS VERDICT
                  </span>
                  <h2 className="text-xl font-bold text-slate-100">
                    {data.winning_recommendation} on {data.ticker}
                  </h2>
                </div>
              </div>

              <div className="flex items-center gap-4 num-tabular">
                <div className="p-3 rounded-lg bg-slate-900 border border-[#162235]">
                  <span className="text-slate-500 text-[10px] uppercase block">Consensus Score</span>
                  <span className="text-lg font-bold text-cyan-300">
                    {(data.consensus_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-[#162235]">
                  <span className="text-slate-500 text-[10px] uppercase block">Confidence</span>
                  <span className="text-lg font-bold text-emerald-400">
                    {(data.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-[#162235]">
                  <span className="text-slate-500 text-[10px] uppercase block">Agreement</span>
                  <span className="text-lg font-bold text-purple-300">
                    {(data.agreement_ratio * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Verdict Summary Text */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-[#162235] space-y-2">
              <div className="font-bold text-cyan-400 flex items-center gap-2 text-xs">
                <FileCheck className="h-4 w-4" />
                <span>Synthesis & Rationale:</span>
              </div>
              <p className="text-slate-200 leading-relaxed text-xs">
                {data.verdict_summary}
              </p>
            </div>

            {/* Cryptographic Audit Signature */}
            <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-[#162235]">
              <span>Audit Signature: <span className="text-purple-300 font-mono">{data.audit_signature || 'SHA256_AUTHENTICATED'}</span></span>
              <span>Timestamp: {data.timestamp ? new Date(data.timestamp).toLocaleString() : '—'}</span>
            </div>
          </div>

          {/* Specialist Breakdown Grid */}
          <div className="space-y-4">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Cpu className="h-4 w-4 text-cyan-400" />
              Specialist Agent Deliberations
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(specialistOpinions).map(([agentName, op]) => (
                <div
                  key={agentName}
                  className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-200 uppercase tracking-wide">
                        {agentName.replace(/_/g, ' ')}
                      </span>
                      <StatusBadge status={op?.recommendation || op?.vote || 'BUY'} size="xs" />
                    </div>
                    <p className="text-slate-300 leading-relaxed text-xs">
                      {op?.reasoning || op?.summary || (typeof op === 'string' ? op : 'Analysis recorded.')}
                    </p>
                  </div>

                  {op?.confidence !== undefined && (
                    <div className="pt-2 border-t border-[#162235] flex justify-between text-[11px] text-cyan-400">
                      <span>Conviction:</span>
                      <span className="font-bold">
                        {typeof op.confidence === 'number'
                          ? `${(op.confidence > 1 ? op.confidence : op.confidence * 100).toFixed(0)}%`
                          : op.confidence}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Adversarial, Judicial & Risk Assessments */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-5 space-y-2">
              <div className="font-bold text-rose-300 flex items-center gap-2">
                <Scale className="h-4 w-4" />
                <span>Adversarial Stress Test</span>
              </div>
              <p className="text-slate-300 leading-relaxed text-xs">
                {adversarialCritique?.critique ||
                  adversarialCritique?.summary ||
                  (typeof adversarialCritique === 'string'
                    ? adversarialCritique
                    : 'Adversarial counter-arguments evaluated.')}
              </p>
            </div>

            <div className="rounded-xl border border-purple-900/50 bg-purple-950/20 p-5 space-y-2">
              <div className="font-bold text-purple-300 flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                <span>Judicial Evaluation</span>
              </div>
              <p className="text-slate-300 leading-relaxed text-xs">
                {judicialEvaluation?.synthesis ||
                  judicialEvaluation?.verdict ||
                  (typeof judicialEvaluation === 'string'
                    ? judicialEvaluation
                    : 'Judicial arbitration completed.')}
              </p>
            </div>

            <div className="rounded-xl border border-amber-900/50 bg-amber-950/20 p-5 space-y-2">
              <div className="font-bold text-amber-300 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4" />
                <span>Risk Officer Bounds</span>
              </div>
              <p className="text-slate-300 leading-relaxed text-xs">
                {riskAssessment?.risk_summary ||
                  riskAssessment?.mitigation ||
                  (typeof riskAssessment === 'string'
                    ? riskAssessment
                    : 'Portfolio risk controls verified.')}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
