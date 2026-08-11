import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Newspaper,
  Search,
  RefreshCw,
  ExternalLink,
  DownloadCloud,
} from 'lucide-react';
import { fetchTickerNews, ingestNews } from '../services/marketService';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { toast } from '../hooks/useToast';

export const NewsPage = () => {
  const queryClient = useQueryClient();
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE.NSE');
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('ALL');

  const {
    data: articles = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['tickerNews', selectedTicker],
    queryFn: () => fetchTickerNews(selectedTicker),
  });

  const ingestMutation = useMutation({
    mutationFn: () => ingestNews([selectedTicker.split('.')[0]]),
    onSuccess: (data) => {
      toast.success('News Ingestion Completed', `Ingested ${data?.ingested_count || 0} articles.`);
      queryClient.invalidateQueries({ queryKey: ['tickerNews', selectedTicker] });
    },
    onError: (err) => {
      toast.error('Ingestion Failed', err.message);
    },
  });

  const filtered = articles.filter((item) => {
    const title = item.title || item.headline || '';
    const summary = item.summary || item.content || '';
    const matchesSearch =
      title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      summary.toLowerCase().includes(searchQuery.toLowerCase());

    const sent = item.sentiment || 'NEUTRAL';
    const matchesSentiment = sentimentFilter === 'ALL' || sent === sentimentFilter;

    return matchesSearch && matchesSentiment;
  });

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              FINANCIAL NEWS & NLP SENTIMENT FEED
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              INTELLIGENCE INGESTION
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Real-time market headlines, financial filings & automated sentiment NLP classification
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => ingestMutation.mutate()}
            isLoading={ingestMutation.isPending}
            leftIcon={<DownloadCloud className="h-3.5 w-3.5" />}
          >
            Ingest Live News
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Control Bar: Ticker Picker, Search, Sentiment Filter */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2 w-full md:w-auto">
          <span className="text-slate-400 font-bold whitespace-nowrap">TICKER:</span>
          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="bg-slate-900 border border-[#162235] rounded-lg px-2.5 py-1.5 text-slate-100 font-bold focus:border-cyan-500"
          >
            <option value="RELIANCE.NSE">RELIANCE</option>
            <option value="TCS.NSE">TCS</option>
            <option value="INFY.NSE">INFY</option>
            <option value="HDFCBANK.NSE">HDFCBANK</option>
            <option value="ICICIBANK.NSE">ICICIBANK</option>
            <option value="SBIN.NSE">SBIN</option>
            <option value="NIFTY.NSE">NIFTY 50</option>
          </select>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto flex-1 max-w-md">
          <div className="relative flex-1">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search news by keyword..."
              className="w-full bg-slate-900 border border-[#162235] rounded-lg pl-8 pr-3 py-1.5 text-slate-100 text-xs focus:border-cyan-500"
            />
          </div>

          <select
            value={sentimentFilter}
            onChange={(e) => setSentimentFilter(e.target.value)}
            className="bg-slate-900 border border-[#162235] rounded-lg px-2.5 py-1.5 text-slate-100 text-xs focus:border-cyan-500"
          >
            <option value="ALL">All Sentiments</option>
            <option value="BULLISH">Bullish</option>
            <option value="BEARISH">Bearish</option>
            <option value="NEUTRAL">Neutral</option>
          </select>
        </div>
      </div>

      {/* Articles Grid */}
      {isLoading ? (
        <LoadingSpinner message={`Fetching intelligence articles for ${selectedTicker}...`} />
      ) : filtered.length === 0 ? (
        <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-12 text-center text-slate-500 space-y-3">
          <Newspaper className="h-8 w-8 text-slate-600 mx-auto" />
          <div className="text-sm font-bold text-slate-300">No News Found for {selectedTicker}</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Click &ldquo;Ingest Live News&rdquo; above to trigger the backend news pipeline to crawl Yahoo Finance and exchange filings.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((item, idx) => {
            return (
              <div
                key={item.id || idx}
                className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-3 flex flex-col justify-between hover:border-[#1f3350] transition-colors"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-bold text-sm text-slate-100 leading-snug">
                      {item.title || item.headline}
                    </h3>
                    <StatusBadge status={item.sentiment || 'NEUTRAL'} size="xs" />
                  </div>

                  <p className="text-slate-300 leading-relaxed text-xs">
                    {item.summary || item.content || 'Article summary text provided by market feed.'}
                  </p>
                </div>

                <div className="pt-3 border-t border-[#162235] flex items-center justify-between text-[11px] text-slate-500">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-400">{item.source || 'NSE'}</span>
                    <span>&bull;</span>
                    <span>{item.timestamp ? new Date(item.timestamp).toLocaleDateString() : 'Recent'}</span>
                  </div>

                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      <span>Read Original</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
