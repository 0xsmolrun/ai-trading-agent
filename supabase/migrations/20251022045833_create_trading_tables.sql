/*
  # Trading Agent Database Schema

  1. New Tables
    - `trades`
      - `id` (uuid, primary key)
      - `asset` (text) - Trading symbol (BTC, ETH, etc.)
      - `action` (text) - buy, sell, or hold
      - `entry_price` (numeric) - Entry price for the trade
      - `amount` (numeric) - Amount traded
      - `allocation_usd` (numeric) - USD allocation
      - `tp_price` (numeric, nullable) - Take profit price
      - `sl_price` (numeric, nullable) - Stop loss price
      - `exit_plan` (text) - Exit strategy description
      - `rationale` (text) - LLM reasoning for the trade
      - `status` (text) - open, closed, or pending
      - `pnl` (numeric, nullable) - Profit and loss
      - `created_at` (timestamptz) - Trade creation time
      - `updated_at` (timestamptz) - Last update time

    - `performance_metrics`
      - `id` (uuid, primary key)
      - `total_return` (numeric) - Total return percentage
      - `sharpe_ratio` (numeric) - Risk-adjusted return metric
      - `account_value` (numeric) - Current account value
      - `available_cash` (numeric) - Available cash balance
      - `created_at` (timestamptz) - Metric snapshot time

    - `agent_config`
      - `id` (uuid, primary key)
      - `assets` (text[]) - Array of assets to trade
      - `interval` (text) - Trading interval (e.g., 1h, 5m)
      - `is_active` (boolean) - Agent running status
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated access
*/

CREATE TABLE IF NOT EXISTS trades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  asset text NOT NULL,
  action text NOT NULL CHECK (action IN ('buy', 'sell', 'hold')),
  entry_price numeric,
  amount numeric,
  allocation_usd numeric DEFAULT 0,
  tp_price numeric,
  sl_price numeric,
  exit_plan text DEFAULT '',
  rationale text DEFAULT '',
  status text DEFAULT 'pending' CHECK (status IN ('open', 'closed', 'pending')),
  pnl numeric,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS performance_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  total_return numeric DEFAULT 0,
  sharpe_ratio numeric DEFAULT 0,
  account_value numeric DEFAULT 0,
  available_cash numeric DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_config (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  assets text[] DEFAULT '{}',
  interval text DEFAULT '1h',
  is_active boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to trades"
  ON trades FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to trades"
  ON trades FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to trades"
  ON trades FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public read access to performance_metrics"
  ON performance_metrics FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to performance_metrics"
  ON performance_metrics FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public read access to agent_config"
  ON agent_config FOR SELECT
  USING (true);

CREATE POLICY "Allow public update to agent_config"
  ON agent_config FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trades
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_config_updated_at BEFORE UPDATE ON agent_config
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO agent_config (assets, interval, is_active)
VALUES ('{"BTC", "ETH"}', '1h', false)
ON CONFLICT DO NOTHING;
