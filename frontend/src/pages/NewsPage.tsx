import React, { useState } from 'react';
import { Newspaper, TrendingUp, TrendingDown, Search, Tag, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';

export const NewsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const newsItems = [
    {
      id: 1,
      title: 'RBI Keeps Repo Rate Unchanged at 6.5%; Signal Support for Capital Expenditure',
      source: 'Economic Times',
      time: '15 mins ago',
      sentiment: 'BULLISH',
      score: +0.84,
      tickers: ['BANKNIFTY', 'HDFCBANK', 'ICICIBANK'],
      summary: 'Reserve Bank of India Monetary Policy Committee voted 5-1 to maintain benchmark repo rate at 6.50%, citing stable inflation projections.',
    },
    {
      id: 2,
      title: 'Reliance Industries Reports Q1 EBITDA Growth of 18% Driven by Retail & Digital Expansion',
      source: 'LiveMint',
      time: '42 mins ago',
      sentiment: 'BULLISH',
      score: +0.91,
      tickers: ['RELIANCE', 'JIO'],
      summary: 'RIL quarterly net profit reached ₹19,850 crore, supported by strong subscriber growth in Jio Platforms and retail store rollouts.',
    },
    {
      id: 3,
      title: 'Global Crude Prices Spike 2.4% Amid Middle East Supply Concerns',
      source: 'Reuters',
      time: '1 hour ago',
      sentiment: 'BEARISH',
      score: -0.65,
      tickers: ['BPCL', 'HPCL', 'IOC'],
      summary: 'Brent crude futures climbed to $84.20 per barrel, raising margin pressures for Indian public sector oil marketing companies.',
    },
    {
      id: 4,
      title: 'Trent Limited Zudio Store Count Crosses 500 Threshold Milestone',
      source: 'Business Standard',
      time: '2 hours ago',
      sentiment: 'BULLISH',
      score: +0.88,
      tickers: ['TRENT'],
      summary: 'Fashion retailer Trent announced rapid footprint expansion, posting strong same-store sales growth across Tier-2 and Tier-3 Indian cities.',
    },
  ];

  const filteredNews = newsItems.filter(
    (n) =>
      n.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.tickers.some((t) => t.toLowerCase().includes(searchTerm.toLowerCase()))
  );

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
            <Newspaper className="h-4 w-4" />
            <span>REALTIME NLP NEWS SENTIMENT ENGINE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Financial News & Sentiment Intelligence</h1>
          <p className="text-xs text-slate-400">Natural language processing sentiment scoring for Indian equity market news feeds.</p>
        </div>

        <div className="relative">
          <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Filter news by ticker or keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-72"
          />
        </div>
      </div>

      {/* News Stream List */}
      <div className="space-y-4">
        {filteredNews.map((item) => {
          const isBull = item.sentiment === 'BULLISH';
          return (
            <div key={item.id} className="glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="font-bold text-slate-300">{item.source}</span>
                    <span>&bull; {item.time}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-100 hover:text-cyan-300 cursor-pointer transition-colors">
                    {item.title}
                  </h3>
                </div>

                <div
                  className={`shrink-0 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 ${
                    isBull
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                  }`}
                >
                  {isBull ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                  <span>{item.sentiment} ({item.score > 0 ? '+' : ''}{item.score})</span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{item.summary}</p>

              <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs">
                <div className="flex items-center gap-2">
                  <Tag className="h-3.5 w-3.5 text-slate-400" />
                  {item.tickers.map((t) => (
                    <span key={t} className="px-2 py-0.5 rounded bg-white/5 text-cyan-300 font-semibold border border-white/5">
                      {t}
                    </span>
                  ))}
                </div>
                <button className="text-slate-400 hover:text-slate-200 flex items-center gap-1 text-[11px]">
                  <span>Full Story</span>
                  <ExternalLink className="h-3 w-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};
