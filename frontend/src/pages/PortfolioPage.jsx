import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PieChart,
  Wallet,
  ShieldCheck,
  RefreshCw,
  PlusCircle,
  TrendingUp,
  AlertCircle,
  ExternalLink,
  Layers,
  Send,
} from 'lucide-react';
import {
  fetchBrokerProfile,
  fetchBrokerFunds,
  fetchBrokerHoldings,
  fetchBrokerOrders,
  fetchBrokerHealth,
  placeBrokerOrder,
} from '../api/broker';
import { StatCard } from '../components/common/StatCard';
import { Table } from '../components/common/Table';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { toast } from '../hooks/useToast';

export const PortfolioPage = () => {
  const queryClient = useQueryClient();
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [orderForm, setOrderForm] = useState({
    symbol: 'RELIANCE',
    exchange: 'NSE',
    transaction_type: 'BUY',
    quantity: 1,
    product: 'CNC',
    order_type: 'MARKET',
    price: 0,
  });

  const { data: brokerHealth, refetch: refetchHealth } = useQuery({
    queryKey: ['brokerHealth'],
    queryFn: () => fetchBrokerHealth(),
  });

  const { data: profile } = useQuery({
    queryKey: ['brokerProfile'],
    queryFn: () => fetchBrokerProfile(),
    enabled: Boolean(brokerHealth?.is_authenticated),
  });

  const { data: funds } = useQuery({
    queryKey: ['brokerFunds'],
    queryFn: () => fetchBrokerFunds(),
  });

  const { data: holdings = [] } = useQuery({
    queryKey: ['brokerHoldings'],
    queryFn: () => fetchBrokerHoldings(),
  });

  const { data: orders = [] } = useQuery({
    queryKey: ['brokerOrders'],
    queryFn: () => fetchBrokerOrders(),
  });

  const orderMutation = useMutation({
    mutationFn: (payload) => placeBrokerOrder(payload),
    onSuccess: (data) => {
      toast.success('Order Submitted', `Order ID: ${data?.order_id || 'OK'}`);
      setIsOrderModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['brokerOrders'] });
      queryClient.invalidateQueries({ queryKey: ['brokerHoldings'] });
      queryClient.invalidateQueries({ queryKey: ['brokerFunds'] });
    },
    onError: (err) => {
      toast.error('Order Failed', err.message || 'Broker rejected order payload');
    },
  });

  const handlePlaceOrder = (e) => {
    e.preventDefault();
    orderMutation.mutate(orderForm);
  };

  const isConnected = Boolean(brokerHealth?.is_authenticated);

  // Calculate total portfolio value and P&L
  const totalInvested = holdings.reduce(
    (acc, h) => acc + (h.quantity || 0) * (h.average_price || 0),
    0
  );
  const totalCurrentValue = holdings.reduce(
    (acc, h) => acc + (h.quantity || 0) * (h.last_price || h.current_price || h.average_price || 0),
    0
  );
  const totalPnL = totalCurrentValue - totalInvested;
  const totalPnLPct = totalInvested > 0 ? (totalPnL / totalInvested) * 100 : 0;

  return (
    <div className="space-y-6 pb-12 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#162235] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight font-mono">
              PORTFOLIO & BROKER EXECUTION
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
              ZERODHA KITE GATEWAY
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Real-time equity holdings, margin ledger, risk boundaries & order dispatch
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="emerald"
            size="sm"
            onClick={() => setIsOrderModalOpen(true)}
            leftIcon={<PlusCircle className="h-3.5 w-3.5" />}
          >
            Place New Order
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetchHealth()}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Sync Broker
          </Button>
        </div>
      </div>

      {/* Broker Connection Status Banner */}
      {!isConnected && (
        <div className="rounded-xl border border-amber-800/60 bg-amber-950/30 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-200">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-amber-400 shrink-0" />
            <div>
              <div className="font-bold text-sm">Zerodha KiteConnect Disconnected</div>
              <div className="text-[11px] text-amber-300/80">
                Connect your Zerodha account in Settings to enable real-time order execution and live holdings sync.
              </div>
            </div>
          </div>
          <a
            href="/settings"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition-colors shrink-0 text-xs"
          >
            <span>Configure Zerodha OAuth</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      )}

      {/* Portfolio Financial Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="TOTAL PORTFOLIO VALUE"
          value={`₹${totalCurrentValue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          change={totalPnLPct}
          changeLabel="Total Return"
          icon={PieChart}
          subtext={`Invested: ₹${totalInvested.toLocaleString('en-IN')}`}
        />

        <StatCard
          title="UNREALIZED P&L"
          value={`₹${Math.abs(totalPnL).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          change={totalPnLPct}
          changeLabel="All Holdings"
          icon={TrendingUp}
          subtext={totalPnL >= 0 ? 'Net Profit' : 'Net Loss'}
        />

        <StatCard
          title="AVAILABLE CASH MARGIN"
          value={`₹${Number(funds?.available_cash || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          icon={Wallet}
          subtext={`Collateral: ₹${Number(funds?.available_collateral || 0).toLocaleString('en-IN')}`}
        />

        <StatCard
          title="BROKER ACCOUNT"
          value={profile?.user_name || (isConnected ? 'ACTIVE' : 'OFFLINE')}
          icon={ShieldCheck}
          subtext={profile?.user_id ? `ID: ${profile.user_id}` : 'Zerodha API'}
        />
      </div>

      {/* Holdings Ledger Table */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Equity Holdings Ledger</h3>
          </div>
          <span className="text-[10px] text-slate-500">
            {holdings.length} Positions Active
          </span>
        </div>

        <Table
          columns={[
            {
              key: 'tradingsymbol',
              header: 'Instrument',
              accessor: (r) => (
                <div>
                  <div className="font-bold text-slate-200">{r.tradingsymbol || r.symbol}</div>
                  <div className="text-[10px] text-slate-500">{r.exchange || 'NSE'}</div>
                </div>
              ),
            },
            { key: 'quantity', header: 'Qty', align: 'right' },
            {
              key: 'average_price',
              header: 'Avg Price',
              align: 'right',
              accessor: (r) => `₹${Number(r.average_price || 0).toLocaleString('en-IN')}`,
            },
            {
              key: 'last_price',
              header: 'LTP',
              align: 'right',
              accessor: (r) => `₹${Number(r.last_price || r.current_price || 0).toLocaleString('en-IN')}`,
            },
            {
              key: 'pnl',
              header: 'P&L (₹)',
              align: 'right',
              accessor: (r) => {
                const pnl = Number(r.pnl || 0);
                const isPnlUp = pnl >= 0;
                return (
                  <span className={isPnlUp ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                    {isPnlUp ? '+' : ''}₹{pnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                );
              },
            },
          ]}
          data={holdings}
          emptyText="No equity holdings reported by broker gateway."
        />
      </div>

      {/* Active Orders Ledger Table */}
      <div className="rounded-xl border border-[#162235] bg-[#0d1524] p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#162235]">
          <div className="flex items-center gap-2">
            <Send className="h-4 w-4 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Broker Order Book & Audit Log</h3>
          </div>
          <span className="text-[10px] text-slate-500">
            {orders.length} Orders Logged
          </span>
        </div>

        <Table
          columns={[
            {
              key: 'order_id',
              header: 'Order ID',
              accessor: (r) => (
                <span className="font-mono text-cyan-300 text-[11px] font-bold">
                  {r.order_id || 'ORD_001'}
                </span>
              ),
            },
            { key: 'tradingsymbol', header: 'Symbol' },
            {
              key: 'transaction_type',
              header: 'Action',
              accessor: (r) => (
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    r.transaction_type === 'BUY'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : 'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}
                >
                  {r.transaction_type}
                </span>
              ),
            },
            { key: 'quantity', header: 'Qty', align: 'right' },
            {
              key: 'price',
              header: 'Price',
              align: 'right',
              accessor: (r) => (r.price ? `₹${Number(r.price).toLocaleString('en-IN')}` : 'MARKET'),
            },
            {
              key: 'status',
              header: 'Status',
              align: 'center',
              accessor: (r) => <StatusBadge status={r.status || 'COMPLETE'} size="xs" />,
            },
            {
              key: 'order_timestamp',
              header: 'Time',
              align: 'right',
              accessor: (r) => (r.order_timestamp ? new Date(r.order_timestamp).toLocaleTimeString() : '—'),
            },
          ]}
          data={orders}
          emptyText="No orders placed in current trading session."
        />
      </div>

      {/* Order Placement Modal */}
      <Modal
        isOpen={isOrderModalOpen}
        onClose={() => setIsOrderModalOpen(false)}
        title="EXECUTE BROKER ORDER"
        subtitle="FastAPI Zerodha Kite Execution Engine"
      >
        <form onSubmit={handlePlaceOrder} className="space-y-4 text-xs font-mono">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Symbol</label>
              <input
                type="text"
                value={orderForm.symbol}
                onChange={(e) => setOrderForm({ ...orderForm, symbol: e.target.value.toUpperCase() })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Exchange</label>
              <select
                value={orderForm.exchange}
                onChange={(e) => setOrderForm({ ...orderForm, exchange: e.target.value })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100"
              >
                <option value="NSE">NSE</option>
                <option value="BSE">BSE</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Action</label>
              <div className="grid grid-cols-2 gap-1 bg-slate-900 p-1 rounded-lg border border-[#162235]">
                <button
                  type="button"
                  onClick={() => setOrderForm({ ...orderForm, transaction_type: 'BUY' })}
                  className={`py-1 rounded font-bold transition-all ${
                    orderForm.transaction_type === 'BUY'
                      ? 'bg-emerald-600 text-slate-950'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  BUY
                </button>
                <button
                  type="button"
                  onClick={() => setOrderForm({ ...orderForm, transaction_type: 'SELL' })}
                  className={`py-1 rounded font-bold transition-all ${
                    orderForm.transaction_type === 'SELL'
                      ? 'bg-rose-600 text-slate-950'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  SELL
                </button>
              </div>
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Quantity</label>
              <input
                type="number"
                min="1"
                value={orderForm.quantity}
                onChange={(e) => setOrderForm({ ...orderForm, quantity: Number(e.target.value) })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Order Type</label>
              <select
                value={orderForm.order_type}
                onChange={(e) => setOrderForm({ ...orderForm, order_type: e.target.value })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100"
              >
                <option value="MARKET">MARKET</option>
                <option value="LIMIT">LIMIT</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Product</label>
              <select
                value={orderForm.product}
                onChange={(e) => setOrderForm({ ...orderForm, product: e.target.value })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100"
              >
                <option value="CNC">CNC (Delivery)</option>
                <option value="MIS">MIS (Intraday)</option>
              </select>
            </div>
          </div>

          {orderForm.order_type === 'LIMIT' && (
            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Limit Price (₹)</label>
              <input
                type="number"
                step="0.05"
                value={orderForm.price}
                onChange={(e) => setOrderForm({ ...orderForm, price: Number(e.target.value) })}
                className="w-full bg-slate-900 border border-[#162235] rounded-lg p-2 text-slate-100 font-bold focus:border-cyan-500"
                required
              />
            </div>
          )}

          <div className="pt-2 flex justify-end gap-2 border-t border-[#162235]">
            <Button variant="outline" size="sm" onClick={() => setIsOrderModalOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant={orderForm.transaction_type === 'BUY' ? 'emerald' : 'destructive'}
              size="sm"
              isLoading={orderMutation.isPending}
            >
              Confirm & Submit Order
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
