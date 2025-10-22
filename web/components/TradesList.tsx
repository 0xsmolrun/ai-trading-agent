import { ArrowUpRight, ArrowDownRight, Clock } from 'lucide-react';

interface TradesListProps {
  trades: any[];
}

export default function TradesList({ trades }: TradesListProps) {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="pb-3">Time</th>
              <th className="pb-3">Asset</th>
              <th className="pb-3">Action</th>
              <th className="pb-3">Entry Price</th>
              <th className="pb-3">Amount</th>
              <th className="pb-3">TP / SL</th>
              <th className="pb-3">PnL</th>
              <th className="pb-3">Status</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {trades.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-gray-400">
                  No trades yet
                </td>
              </tr>
            ) : (
              trades.map((trade) => (
                <tr
                  key={trade.id}
                  className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
                >
                  <td className="py-3 flex items-center gap-2 text-gray-400">
                    <Clock className="w-4 h-4" />
                    {new Date(trade.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-3 font-semibold">{trade.asset}</td>
                  <td className="py-3">
                    <span
                      className={`flex items-center gap-1 w-fit px-2 py-1 rounded text-xs ${
                        trade.action === 'buy'
                          ? 'bg-green-500/20 text-green-400'
                          : trade.action === 'sell'
                          ? 'bg-red-500/20 text-red-400'
                          : 'bg-gray-500/20 text-gray-400'
                      }`}
                    >
                      {trade.action === 'buy' ? (
                        <ArrowUpRight className="w-3 h-3" />
                      ) : trade.action === 'sell' ? (
                        <ArrowDownRight className="w-3 h-3" />
                      ) : null}
                      {trade.action.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3">${trade.entry_price?.toFixed(2) || '0.00'}</td>
                  <td className="py-3">{trade.amount?.toFixed(4) || '0.0000'}</td>
                  <td className="py-3 text-xs text-gray-400">
                    {trade.tp_price && trade.sl_price
                      ? `$${trade.tp_price.toFixed(2)} / $${trade.sl_price.toFixed(2)}`
                      : 'N/A'}
                  </td>
                  <td className="py-3">
                    <span
                      className={`font-medium ${
                        trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {trade.pnl >= 0 ? '+' : ''}
                      {trade.pnl?.toFixed(2) || '0.00'}%
                    </span>
                  </td>
                  <td className="py-3">
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        trade.status === 'open'
                          ? 'bg-blue-500/20 text-blue-400'
                          : trade.status === 'closed'
                          ? 'bg-gray-500/20 text-gray-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}
                    >
                      {trade.status || 'pending'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
