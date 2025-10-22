import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import Dashboard from './components/Dashboard';
import Controls from './components/Controls';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default function App() {
  const [agentStatus, setAgentStatus] = useState<'running' | 'stopped'>('stopped');
  const [trades, setTrades] = useState<any[]>([]);
  const [performance, setPerformance] = useState<any>(null);

  useEffect(() => {
    loadData();
    checkAgentStatus();
    const interval = setInterval(() => {
      loadData();
      checkAgentStatus();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkAgentStatus = async () => {
    try {
      const { data } = await supabase
        .from('agent_config')
        .select('is_active')
        .limit(1)
        .maybeSingle();

      if (data) {
        setAgentStatus(data.is_active ? 'running' : 'stopped');
      }
    } catch (error) {
      console.error('Error checking agent status:', error);
    }
  };

  const loadData = async () => {
    try {
      const { data: tradesData } = await supabase
        .from('trades')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50);

      if (tradesData) {
        setTrades(tradesData);
      }

      const { data: perfData } = await supabase
        .from('performance_metrics')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle();

      if (perfData) {
        setPerformance(perfData);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleStatusChange = async (newStatus: 'running' | 'stopped') => {
    try {
      const action = newStatus === 'running' ? 'start' : 'stop';
      const apiUrl = `${supabaseUrl}/functions/v1/trading-agent?action=${action}`;

      await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${supabaseAnonKey}`,
          'Content-Type': 'application/json',
        },
      });

      setAgentStatus(newStatus);
    } catch (error) {
      console.error('Error changing agent status:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                Nocturne AI Trading Agent
              </h1>
              <p className="text-gray-400 text-sm mt-1">
                Autonomous trading powered by LLMs on Hyperliquid
              </p>
            </div>
            <Controls
              status={agentStatus}
              onStatusChange={handleStatusChange}
            />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <Dashboard
          trades={trades}
          performance={performance}
        />
      </main>
    </div>
  );
}
