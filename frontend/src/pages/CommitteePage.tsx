import React, { useState } from 'react';
import { BrainCircuit, Cpu, ShieldAlert, BarChart3, CheckCircle2, Play, Users, MessageSquare } from 'lucide-react';
import { AICommitteeWidget } from '../components/common/AICommitteeWidget';
import { motion } from 'framer-motion';

export const CommitteePage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono"
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2 text-xs text-purple-400 font-semibold mb-1">
            <BrainCircuit className="h-4 w-4" />
            <span>MULTI-AGENT AI CONSENSUS CHAMBER</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">AI Investment Committee</h1>
          <p className="text-xs text-slate-400">Autonomous multi-agent deliberation, risk voting, and portfolio position sizing.</p>
        </div>
      </div>

      {/* Main Grid Widget + Live Agent Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <AICommitteeWidget />

          {/* Committee Audit History */}
          <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-purple-400" />
              Recent Committee Deliberation Minutes
            </h3>

            <div className="space-y-3">
              {[
                { date: '2026-07-31 10:30 AM', target: 'RELIANCE', outcome: 'LONG ALLOCATION (+2.5%)', conviction: '92%', status: 'APPROVED' },
                { date: '2026-07-30 02:15 PM', target: 'TRENT', outcome: 'HOLD POSITION (Cap 5%)', conviction: '84%', status: 'APPROVED' },
                { date: '2026-07-29 11:00 AM', target: 'DELHIVERY', outcome: 'REDUCE ALLOCATION (-1.0%)', conviction: '76%', status: 'REJECTED' },
              ].map((item, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 font-bold text-slate-100 text-xs">
                      <span>{item.target}</span>
                      <span className="text-[10px] text-slate-400">&bull; {item.date}</span>
                    </div>
                    <div className="text-xs text-slate-300">{item.outcome}</div>
                  </div>

                  <div className="text-right space-y-1">
                    <div className="text-xs font-bold text-purple-300">Conviction: {item.conviction}</div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar Agent Profiles */}
        <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
            <Users className="h-4 w-4 text-purple-400" />
            Committee Roster
          </h3>

          <div className="space-y-3">
            {[
              { name: 'Macro Strategist', model: 'Gemini 1.5 Pro', specialization: 'RBI Rates, Fed Liquidity, Inflation' },
              { name: 'Quant Factor Agent', model: 'Claude 3.5 Sonnet', specialization: 'DCF, ROIC, Earnings Surprises' },
              { name: 'Technical Analyst', model: 'GPT-4o Quant', specialization: 'VWAP, Momentum Breakouts, RSI' },
              { name: 'Chief Risk Officer', model: 'DeepSeek R1', specialization: 'VaR 95%, Portfolio Beta, Stop Losses' },
            ].map((agent, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1 text-xs">
                <div className="font-bold text-slate-200">{agent.name}</div>
                <div className="text-[10px] text-purple-300 font-semibold">{agent.model}</div>
                <div className="text-[11px] text-slate-400">{agent.specialization}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
