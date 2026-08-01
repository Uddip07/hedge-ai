import React, { useState } from 'react';
import { SearchCode, Send, Sparkles, FileText, Bookmark, Bot, User } from 'lucide-react';
import { motion } from 'framer-motion';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  citations?: string[];
  timestamp: string;
}

export const ResearchPage: React.FC = () => {
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: 'Welcome to the MONEYYYYYY Deep RAG Investment Research Assistant. Ask any question regarding Indian equities, RBI monetary stance, sector balance sheets, or SEC/NSE financial filings.',
      timestamp: '10:45 AM',
    },
  ]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputQuery,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');

    // Simulate RAG AI Response
    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: `Based on vector search retrieval across recent Q1 FY26 transcripts and balance sheet filings, Trent Limited (TRENT) demonstrates industry-leading store productivity. Operating margins expanded by 180 bps YoY to 16.5%.`,
        citations: ['Trent_Q1_2026_Transcript.pdf', 'NSE_Retail_Sector_Audit.pdf'],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    }, 1200);
  };

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
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <SearchCode className="h-4 w-4" />
            <span>VECTOR STORE DEEP RAG ENGINE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Deep RAG Investment Research</h1>
          <p className="text-xs text-slate-400">Contextual document retrieval across SEC filings, earnings transcripts, and equity research reports.</p>
        </div>
      </div>

      {/* Main Grid Chat + Citations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Stream Column */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 border border-white/10 flex flex-col h-[600px]">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto space-y-4 pr-2">
            {messages.map((m) => (
              <div key={m.id} className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.sender === 'ai' && (
                  <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 h-fit">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-xl p-4 rounded-2xl text-xs space-y-2 leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/40 rounded-tr-none'
                      : 'bg-white/5 text-slate-200 border border-white/10 rounded-tl-none'
                  }`}
                >
                  <p>{m.text}</p>
                  {m.citations && (
                    <div className="pt-2 border-t border-white/10 flex flex-wrap gap-1.5 text-[10px]">
                      <span className="text-slate-400">Sources:</span>
                      {m.citations.map((c, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-white/5 text-cyan-300 border border-white/10 flex items-center gap-1">
                          <FileText className="h-3 w-3" />
                          {c}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="text-[9px] text-slate-500 text-right">{m.timestamp}</div>
                </div>

                {m.sender === 'user' && (
                  <div className="p-2 rounded-xl bg-white/10 border border-white/10 text-slate-300 h-fit">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSend} className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <input
              type="text"
              placeholder="Ask RAG assistant about balance sheets, ROCE, or SEC transcripts..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
            />
            <button
              type="submit"
              className="p-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition-all shadow-lg shadow-cyan-950/50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>

        {/* Vector Knowledge Index Sidebar */}
        <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
          <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2 border-b border-white/10 pb-3">
            <Bookmark className="h-4 w-4 text-cyan-400" />
            Indexed Knowledge Vector Stores
          </h3>

          <div className="space-y-3 text-xs">
            {[
              { doc: 'RBI_Monetary_Policy_Jul2026.pdf', chunks: 142, status: 'INDEXED' },
              { doc: 'NSE_Top50_Q1_Transcripts.pdf', chunks: 890, status: 'INDEXED' },
              { doc: 'Indian_Macro_Liquidity_Report.pdf', chunks: 215, status: 'INDEXED' },
            ].map((d, i) => (
              <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                <div className="font-bold text-slate-200 truncate">{d.doc}</div>
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>{d.chunks} vector chunks</span>
                  <span className="text-emerald-400 font-semibold">{d.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
