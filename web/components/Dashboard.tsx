import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react';
import PerformanceChart from './PerformanceChart';
import TradesList from './TradesList';
import PositionsPanel from './PositionsPanel';

interface DashboardProps {
  trades: any[];
  performance: any;
}

export default function Dashboard({ trades, performance }: DashboardProps) {
  const totalReturn = performance?.total_return || 0;
  const sharpeRatio = performance?.sharpe_ratio || 0;
  const accountValue = performance?.account_value || 0;
  const availableCash = performance?.available_cash || 0;

  const stats = [
    {
      label: 'Total Return',
      value: `${totalReturn >= 0 ? '+' : ''}${totalReturn.toFixed(2)}%`,
      icon: totalReturn >= 0 ? TrendingUp : TrendingDown,
      color: totalReturn >= 0 ? 'text-green-400' : 'text-red-400',
      bgColor: totalReturn >= 0 ? 'bg-green-400/10' : 'bg-red-400/10',
    },
    {
      label: 'Sharpe Ratio',
      value: sharpeRatio.toFixed(3),
      icon: Activity,
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/10',
    },
    {
      label: 'Account Value',
      value: `$${accountValue.toLocaleString()}`,
      icon: DollarSign,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-400/10',
    },
    {
      label: 'Available Cash',
      value: `$${availableCash.toLocaleString()}`,
      icon: DollarSign,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-400/10',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-gray-600 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">{stat.label}</p>
                <p className={`text-2xl font-bold mt-1 ${stat.color}`}>
                  {stat.value}
                </p>
              </div>
              <div className={`${stat.bgColor} p-3 rounded-lg`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PerformanceChart trades={trades} />
        </div>
        <div className="lg:col-span-1">
          <PositionsPanel trades={trades.filter(t => t.status === 'open')} />
        </div>
      </div>

      <TradesList trades={trades} />
    </div>
  );
}
