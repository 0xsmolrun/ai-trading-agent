import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface PerformanceChartProps {
  trades: any[];
}

export default function PerformanceChart({ trades }: PerformanceChartProps) {
  const chartData = trades
    .slice(0, 20)
    .reverse()
    .map((trade, index) => ({
      index,
      value: trade.pnl || 0,
      timestamp: new Date(trade.created_at).toLocaleTimeString(),
    }));

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4">Performance Overview</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="timestamp" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={{ fill: '#3B82F6' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
