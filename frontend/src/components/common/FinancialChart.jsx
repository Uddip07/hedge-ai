import React, { useState, memo } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { BarChart2, Layers, RefreshCw } from 'lucide-react';

export const FinancialChart = memo(
  ({ data = [], symbol = 'NIFTY.NSE', quote = null, height = 360, isLoading = false }) => {
    const [timeframe, setTimeframe] = useState('ALL');
    const [showVolume, setShowVolume] = useState(true);
    const [showSMA, setShowSMA] = useState(true);

    if (isLoading) {
      return (
        <div
          className="rounded-xl border border-[#162235] bg-[#0d1524] p-8 flex flex-col items-center justify-center text-slate-400 font-mono text-xs w-full"
          style={{ height }}
        >
          <RefreshCw className="h-6 w-6 mb-2 animate-spin text-cyan-400" />
          <span>Loading market price history for {symbol}...</span>
        </div>
      );
    }

    if (!data || data.length === 0) {
      return (
        <div
          className="rounded-xl border border-[#162235] bg-[#0d1524] p-8 flex flex-col items-center justify-center text-slate-500 font-mono text-xs w-full"
          style={{ height }}
        >
          <BarChart2 className="h-8 w-8 mb-2 text-cyan-500/40" />
          <span className="font-semibold text-slate-400">NO DATA AVAILABLE</span>
          <span className="text-[11px] text-slate-600 mt-1">No historical price candles returned for {symbol}</span>
        </div>
      );
    }

    // Filter by timeframe
    let filteredData = [...data];
    if (timeframe === '1D' && filteredData.length > 1) {
      filteredData = filteredData.slice(-1);
    } else if (timeframe === '1W' && filteredData.length > 5) {
      filteredData = filteredData.slice(-5);
    } else if (timeframe === '1M' && filteredData.length > 22) {
      filteredData = filteredData.slice(-22);
    } else if (timeframe === '1Y' && filteredData.length > 252) {
      filteredData = filteredData.slice(-252);
    }

    // Calculate 20-period SMA safely
    const chartDataWithSMA = filteredData.map((d, i, arr) => {
      const closeNum = typeof d.close === 'number' ? d.close : parseFloat(d.close || 0);
      let sma20 = null;
      if (i >= 19) {
        const slice = arr.slice(i - 19, i + 1);
        sma20 = slice.reduce((acc, curr) => {
          const c = typeof curr.close === 'number' ? curr.close : parseFloat(curr.close || 0);
          return acc + c;
        }, 0) / 20;
      }
      return {
        ...d,
        close: closeNum,
        sma20: sma20 ? Number(sma20.toFixed(2)) : null,
      };
    });

    const candleLastPrice = Number(chartDataWithSMA[chartDataWithSMA.length - 1]?.close || 0);
    const displayPrice = (quote && typeof quote.price === 'number' && quote.price > 0)
      ? quote.price
      : (candleLastPrice > 0 ? candleLastPrice : null);

    const firstPrice = Number(chartDataWithSMA[0]?.close || 0);
    const priceChange = (quote && typeof quote.change === 'number')
      ? quote.change
      : (displayPrice && firstPrice ? displayPrice - firstPrice : 0);

    const pctChange = (quote && typeof quote.change_percent === 'number')
      ? quote.change_percent
      : (firstPrice > 0 ? (priceChange / firstPrice) * 100 : 0);

    const isPositive = priceChange >= 0;
    const strokeColor = isPositive ? '#10b981' : '#f43f5e';

    return (
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-4 flex flex-col relative overflow-hidden w-full min-w-0 font-mono shadow-xl">
        {/* Header Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-sm text-slate-100">{symbol}</span>
              <span className="text-[10px] font-mono text-cyan-400 font-semibold px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/60">
                NSE/BSE OHLCV
              </span>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono num-tabular">
              <span className="font-bold text-slate-100 text-sm">
                {displayPrice !== null
                  ? `₹${displayPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                  : '—'}
              </span>
              {displayPrice !== null && (
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded ${
                    isPositive
                      ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                      : 'bg-rose-950/80 text-rose-400 border border-rose-800/60'
                  }`}
                >
                  {isPositive ? '+' : ''}
                  {pctChange.toFixed(2)}%
                </span>
              )}
            </div>
          </div>

          {/* Timeframe & Overlay Controls */}
          <div className="flex items-center gap-1 text-xs bg-slate-900/80 p-1 rounded-lg border border-slate-800">
            {['1D', '1W', '1M', '1Y', 'ALL'].map((tf) => (
              <button
                key={tf}
                type="button"
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 rounded transition-all font-semibold cursor-pointer ${
                  timeframe === tf
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {tf}
              </button>
            ))}
            <button
              type="button"
              onClick={() => setShowSMA(!showSMA)}
              className={`px-2 py-1 rounded ml-1 text-[11px] font-semibold transition-colors cursor-pointer ${
                showSMA ? 'text-amber-300 bg-amber-950/50 border border-amber-800/50' : 'text-slate-500'
              }`}
              title="Toggle 20 SMA"
            >
              SMA20
            </button>
            <button
              type="button"
              onClick={() => setShowVolume(!showVolume)}
              className={`p-1 rounded ml-0.5 transition-colors cursor-pointer ${
                showVolume ? 'text-cyan-400 bg-cyan-950/50 border border-cyan-800/50' : 'text-slate-500'
              }`}
              title="Toggle Volume Bars"
            >
              <Layers className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Chart Canvas */}
        <div className="mt-4 w-full min-w-0" style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartDataWithSMA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id={`colorPrice_${symbol}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={strokeColor} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={strokeColor} stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#162235" vertical={false} />

              <XAxis
                dataKey="date"
                stroke="#64748B"
                fontSize={10}
                fontFamily="JetBrains Mono"
                tickLine={false}
                axisLine={false}
                tickFormatter={(d) => {
                  if (typeof d !== 'string') return String(d || '');
                  if (d.length >= 10 && d.includes('-')) return d.slice(5);
                  return d;
                }}
              />

              <YAxis
                yAxisId="price"
                domain={['auto', 'auto']}
                stroke="#64748B"
                fontSize={10}
                fontFamily="JetBrains Mono"
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `₹${val}`}
              />

              {showVolume && (
                <YAxis yAxisId="volume" orientation="right" domain={[0, 'auto']} hide={true} />
              )}

              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload || !payload.length) return null;
                  const d = payload[0]?.payload;
                  if (!d) return null;
                  return (
                    <div className="bg-[#090e17] p-3 rounded-lg text-xs font-mono border border-cyan-500/40 shadow-2xl space-y-1 z-50">
                      <div className="text-slate-400 border-b border-[#162235] pb-1 font-semibold flex justify-between">
                        <span>{d.date}</span>
                        {d.sma20 && <span className="text-amber-400">SMA: ₹{d.sma20}</span>}
                      </div>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-slate-200">
                        <span className="text-slate-400">Open:</span>
                        <span className="font-bold text-right num-tabular">₹{d.open}</span>
                        <span className="text-slate-400">High:</span>
                        <span className="font-bold text-right num-tabular text-emerald-400">₹{d.high}</span>
                        <span className="text-slate-400">Low:</span>
                        <span className="font-bold text-right num-tabular text-rose-400">₹{d.low}</span>
                        <span className="text-slate-400">Close:</span>
                        <span className="font-bold text-right num-tabular text-cyan-300">₹{d.close}</span>
                        {d.volume !== undefined && (
                          <>
                            <span className="text-slate-400">Volume:</span>
                            <span className="font-bold text-right num-tabular text-slate-300">
                              {Number(d.volume).toLocaleString('en-IN')}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  );
                }}
              />

              <Area
                yAxisId="price"
                type="monotone"
                dataKey="close"
                stroke={strokeColor}
                strokeWidth={2}
                fillOpacity={1}
                fill={`url(#colorPrice_${symbol})`}
              />

              {showSMA && (
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="sma20"
                  stroke="#f59e0b"
                  strokeWidth={1.5}
                  dot={false}
                  name="SMA 20"
                />
              )}

              {showVolume && (
                <Bar
                  yAxisId="volume"
                  dataKey="volume"
                  fill="rgba(6, 182, 212, 0.25)"
                  radius={[2, 2, 0, 0]}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }
);

FinancialChart.displayName = 'FinancialChart';
