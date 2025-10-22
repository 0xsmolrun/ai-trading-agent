import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface PositionsPanelProps {
  trades: any[];
}

export default function PositionsPanel({ trades }: PositionsPanelProps) {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4">Open Positions</h2>
      <div className="space-y-3">
        {trades.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">
            No open positions
          </p>
        ) : (
          trades.slice(0, 5).map((trade) => (
            <div
              key={trade.id}
              className="bg-gray-900/50 rounded-lg p-4 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-lg">{trade.asset}</span>
                  <span
                    className={`flex items-center gap-1 text-xs px-2 py-1 rounded ${
                      trade.action === 'buy'
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}
                  >
                    {trade.action === 'buy' ? (
                      <ArrowUpRight className="w-3 h-3" />
                    ) : (
                      <ArrowDownRight className="w-3 h-3" />
                    )}
                    {trade.action.toUpperCase()}
                  </span>
                </div>
                <span
                  className={`text-sm font-medium ${
                    trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {trade.pnl >= 0 ? '+' : ''}
                  {trade.pnl?.toFixed(2) || '0.00'}%
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                <div>
                  <span className="block">Entry</span>
                  <span className="text-white font-medium">
                    ${trade.entry_price?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div>
                  <span className="block">Amount</span>
                  <span className="text-white font-medium">
                    {trade.amount?.toFixed(4) || '0.0000'}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
