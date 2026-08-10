import React, { useState, memo } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { BarChart2, Layers, RefreshCw } from 'lucide-react';

interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma20?: number;
}

interface FinancialChartProps {
  data: ChartDataPoint[];
  symbol: string;
  height?: number;
  isLoading?: boolean;
}

export const FinancialChart: React.FC<FinancialChartProps> = memo(
  ({ data, symbol, height = 360, isLoading = false }) => {
    const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '1Y' | 'ALL'>('1M');
    const [showVolume, setShowVolume] = useState(true);

    if (isLoading) {
      return (
        <div
          className="bg-[#121826] border border-[#1E293B] rounded-xl p-8 flex flex-col items-center justify-center text-slate-400 font-mono text-xs w-full"
          style={{ height }}
        >
          <RefreshCw className="h-6 w-6 mb-2 animate-spin text-cyan-400" />
          <span>Loading backend market history for {symbol}...</span>
        </div>
      );
    }

    if (!data || data.length === 0) {
      return (
        <div
          className="bg-[#121826] border border-[#1E293B] rounded-xl p-8 flex flex-col items-center justify-center text-slate-500 font-mono text-xs w-full"
          style={{ height }}
        >
          <BarChart2 className="h-8 w-8 mb-2 animate-pulse text-cyan-500/40" />
          <span>No market history data returned for {symbol}</span>
        </div>
      );
    }

    const firstPrice = data[0]?.close || 0;
    const lastPrice = data[data.length - 1]?.close || 0;
    const priceChange = lastPrice - firstPrice;
    const pctChange = firstPrice > 0 ? (priceChange / firstPrice) * 100 : 0;
    const isPositive = priceChange >= 0;

    const strokeColor = isPositive ? '#00E676' : '#FF1744';

    return (
      <div className="bg-[#121826] border border-[#1E293B] rounded-xl p-4 flex flex-col relative overflow-hidden w-full min-w-0">
        {/* Header Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#1E293B]">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-base text-slate-100">{symbol}</span>
              <span className="text-[10px] font-mono text-slate-400 font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                NSE EQUITIES
              </span>
            </div>

            <div className="flex items-center gap-2 text-sm font-mono num-tabular">
              <span className="font-bold text-slate-100">
                ₹{lastPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  isPositive
                    ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40'
                    : 'bg-red-950/60 text-red-400 border border-red-800/40'
                }`}
              >
                {isPositive ? '+' : ''}
                {pctChange.toFixed(2)}%
              </span>
            </div>
          </div>

          {/* Timeframe Buttons */}
          <div className="flex items-center gap-1 font-mono text-xs bg-slate-900 p-1 rounded-lg border border-slate-800">
            {(['1D', '1W', '1M', '1Y', 'ALL'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 rounded transition-all font-semibold ${
                  timeframe === tf
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {tf}
              </button>
            ))}
            <button
              onClick={() => setShowVolume(!showVolume)}
              className={`p-1 rounded ml-1 ${
                showVolume ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-500'
              }`}
              title="Toggle Volume Bars"
            >
              <Layers className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Chart Canvas */}
        <div className="mt-4 w-full min-w-0" style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id={`colorPrice_${symbol}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={strokeColor} stopOpacity={0.35} />
                  <stop offset="95%" stopColor={strokeColor} stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />

              <XAxis
                dataKey="date"
                stroke="#64748B"
                fontSize={11}
                fontFamily="JetBrains Mono"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                yAxisId="price"
                domain={['auto', 'auto']}
                stroke="#64748B"
                fontSize={11}
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
                  const d = payload[0].payload as ChartDataPoint;
                  return (
                    <div className="bg-[#121826] p-3 rounded-lg text-xs font-mono border border-cyan-500/30 shadow-2xl space-y-1">
                      <div className="text-slate-400 border-b border-slate-800 pb-1 font-semibold">
                        {d.date}
                      </div>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-slate-200">
                        <span>Open:</span>{' '}
                        <span className="font-bold text-right num-tabular">₹{d.open}</span>
                        <span>High:</span>{' '}
                        <span className="font-bold text-right num-tabular text-emerald-400">
                          ₹{d.high}
                        </span>
                        <span>Low:</span>{' '}
                        <span className="font-bold text-right num-tabular text-red-400">
                          ₹{d.low}
                        </span>
                        <span>Close:</span>{' '}
                        <span className="font-bold text-right num-tabular text-cyan-300">
                          ₹{d.close}
                        </span>
                        <span>Volume:</span>{' '}
                        <span className="font-bold text-right num-tabular">
                          {d.volume.toLocaleString('en-IN')}
                        </span>
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

              {showVolume && (
                <Bar
                  yAxisId="volume"
                  dataKey="volume"
                  fill="rgba(0, 176, 255, 0.25)"
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
