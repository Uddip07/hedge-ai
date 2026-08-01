import React, { useState } from 'react';
import { BrainCircuit, ShieldAlert, Cpu, BarChart3, CheckCircle2, AlertTriangle, Play } from 'lucide-react';
import { motion } from 'framer-motion';

interface AgentVote {
  id: string;
  name: string;
  role: string;
  icon: any;
  vote: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  conviction: number; // 0 - 100
  reasoning: string;
}

export const AICommitteeWidget: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string>('macro');

  const agents: AgentVote[] = [
    {
      id: 'macro',
      name: 'Macro Strategist Agent',
      role: 'RBI Policy & Liquidity Analysis',
      icon: Cpu,
      vote: 'BULLISH',
      conviction: 88,
      reasoning: 'RBI rate pause cycle supports capital goods & banking sector expansion. FII inflows accelerating.',
    },
    {
      id: 'quant',
      name: 'Quant Factor Agent',
      role: 'Valuation & Earnings Momentum',
      icon: BarChart3,
      vote: 'BULLISH',
      conviction: 92,
      reasoning: 'ROCE > 22%, EV/EBITDA trading at 1.2x 5-yr historical median. Strong earnings surprise factor.',
    },
    {
      id: 'risk',
      name: 'Chief Risk Officer',
      role: 'Portfolio VaR & Drawdown Guard',
      icon: ShieldAlert,
      vote: 'NEUTRAL',
      conviction: 74,
      reasoning: 'High concentration in Banking sector. Recommend 4.5% position cap to maintain max 1.2 Beta boundary.',
    },
  ];

  const handleRunDeliberation = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 1800);
  };

  const activeAgent = agents.find((a) => a.id === selectedAgent) || agents[0];

  return (
    <div className="glass-panel rounded-xl p-5 relative overflow-hidden flex flex-col gap-4">
      {/* Top Bar Header */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
            <BrainCircuit className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-mono font-bold text-sm text-slate-100 flex items-center gap-2">
              Multi-Agent Investment Committee
              <span className="px-2 py-0.5 rounded-full text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/40">
                LIVE REASONING
              </span>
            </h3>
            <p className="text-xs text-slate-400">Consensus Engine & Multi-Agent Conviction Matrix</p>
          </div>
        </div>

        <button
          onClick={handleRunDeliberation}
          disabled={isAnalyzing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-mono font-semibold transition-all disabled:opacity-50"
        >
          <Play className={`h-3.5 w-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
          <span>{isAnalyzing ? 'Deliberating...' : 'Trigger Vote'}</span>
        </button>
      </div>

      {/* Agents Voting Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {agents.map((agent) => {
          const IconComponent = agent.icon;
          const isSelected = selectedAgent === agent.id;
          const isBull = agent.vote === 'BULLISH';
          const isBear = agent.vote === 'BEARISH';

          return (
            <motion.div
              key={agent.id}
              onClick={() => setSelectedAgent(agent.id)}
              whileHover={{ y: -2 }}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-cyan-950/30 border-cyan-500/50 shadow-lg shadow-cyan-950/40'
                  : 'bg-white/5 border-white/5 hover:border-white/15'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <IconComponent className="h-4 w-4 text-cyan-400" />
                  <span className="font-mono text-xs font-bold text-slate-200 truncate">{agent.name}</span>
                </div>
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${
                    isBull
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : isBear
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  }`}
                >
                  {agent.vote}
                </span>
              </div>

              <div className="text-[11px] text-slate-400 truncate mb-2">{agent.role}</div>

              {/* Conviction Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] font-mono text-slate-400">
                  <span>Conviction</span>
                  <span className="font-bold text-slate-200">{agent.conviction}%</span>
                </div>
                <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${isBull ? 'bg-emerald-400' : isBear ? 'bg-rose-400' : 'bg-amber-400'}`}
                    style={{ width: `${agent.conviction}%` }}
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Detailed Thought Process Accordion */}
      <div className="bg-white/5 rounded-xl p-4 border border-white/5 space-y-2 font-mono">
        <div className="flex items-center justify-between text-xs text-slate-300 font-semibold border-b border-white/5 pb-2">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            Active Agent Reasoning Log: {activeAgent.name}
          </span>
          <span className="text-[11px] text-cyan-400">Conviction: {activeAgent.conviction}%</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed pt-1">{activeAgent.reasoning}</p>
      </div>
    </div>
  );
};
