import React, { useState } from 'react';
import { Newspaper, TrendingUp, TrendingDown, Search, Tag, ExternalLink } from 'lucide-react';
import { NewsItem } from '../types/api';

export const NewsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const newsItems: NewsItem[] = [
    {
      id: '1',
      title: 'RBI Keeps Repo Rate Unchanged at 6.5%; Signal Support for Capital Expenditure',
      source: 'Economic Times',
      timestamp: '15 mins ago',
      sentiment: 'BULLISH',
      impact_score: 0.84,
      url: 'https://economictimes.indiatimes.com',
      tickers: ['BANKNIFTY', 'HDFCBANK', 'ICICIBANK'],
      summary:
        'Reserve Bank of India Monetary Policy Committee voted 5-1 to maintain benchmark repo rate at 6.50%, citing stable inflation projections.',
    },
    {
      id: '2',
      title: 'Reliance Industries Reports Q1 EBITDA Growth of 18% Driven by Retail & Digital Expansion',
      source: 'LiveMint',
      timestamp: '42 mins ago',
      sentiment: 'BULLISH',
      impact_score: 0.91,
      url: 'https://livemint.com',
      tickers: ['RELIANCE', 'JIO'],
      summary:
        'RIL quarterly net profit reached ₹19,850 crore, supported by strong subscriber growth in Jio Platforms and retail store rollouts.',
    },
    {
      id: '3',
      title: 'Global Crude Prices Spike 2.4% Amid Middle East Supply Concerns',
      source: 'Reuters',
      timestamp: '1 hour ago',
      sentiment: 'BEARISH',
      impact_score: -0.65,
      url: 'https://reuters.com',
      tickers: ['BPCL', 'HPCL', 'IOC'],
      summary:
        'Brent crude futures climbed to $84.20 per barrel, raising margin pressures for Indian public sector oil marketing companies.',
    },
    {
      id: '4',
      title: 'Trent Limited Zudio Store Count Crosses 500 Threshold Milestone',
      source: 'Business Standard',
      timestamp: '2 hours ago',
      sentiment: 'BULLISH',
      impact_score: 0.88,
      url: 'https://business-standard.com',
      tickers: ['TRENT'],
      summary:
        'Fashion retailer Trent announced rapid footprint expansion, posting strong same-store sales growth across Tier-2 and Tier-3 Indian cities.',
    },
  ];

  const filteredNews = newsItems.filter(
    (n) =>
      n.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.tickers.some((t) => t.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6 w-full max-w-full min-w-0 font-mono">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#121826] p-5 rounded-2xl border border-[#1E293B]">
        <div>
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-semibold mb-1">
            <Newspaper className="h-4 w-4" />
            <span>REALTIME NLP NEWS SENTIMENT ENGINE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Financial News & Sentiment Intelligence</h1>
          <p className="text-xs text-slate-400">
            Natural language processing sentiment scoring for Indian equity market news feeds.
          </p>
        </div>

        <div className="relative">
          <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Filter news by ticker or keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-slate-900 border border-[#1E293B] rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-64 md:w-72"
          />
        </div>
      </div>

      {/* News Stream List */}
      <div className="space-y-4">
        {filteredNews.map((item) => {
          const isBull = item.sentiment === 'BULLISH';
          return (
            <div
              key={item.id}
              className="bg-[#121826] hover:bg-slate-800/40 rounded-2xl p-5 border border-[#1E293B] space-y-3 transition-colors min-w-0"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1 min-w-0 flex-1">
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="font-bold text-slate-300">{item.source}</span>
                    <span>&bull; {item.timestamp}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-100 hover:text-cyan-300 cursor-pointer transition-colors leading-tight">
                    {item.title}
                  </h3>
                </div>

                <div
                  className={`shrink-0 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 ${
                    isBull
                      ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                      : 'bg-red-950/80 text-red-300 border border-red-800/60'
                  }`}
                >
                  {isBull ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                  <span>
                    {item.sentiment} ({item.impact_score > 0 ? '+' : ''}
                    {item.impact_score})
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{item.summary}</p>

              <div className="flex items-center justify-between pt-2 border-t border-[#1E293B] text-xs">
                <div className="flex items-center gap-2 flex-wrap">
                  <Tag className="h-3.5 w-3.5 text-slate-400" />
                  {item.tickers.map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 rounded bg-slate-900 text-cyan-300 font-semibold border border-slate-800 text-[11px]"
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-slate-400 hover:text-slate-200 flex items-center gap-1 text-[11px] shrink-0"
                >
                  <span>Full Story</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
