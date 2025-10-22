import { createClient } from 'npm:@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
};

interface TradeData {
  asset: string;
  action: 'buy' | 'sell' | 'hold';
  entry_price?: number;
  amount?: number;
  allocation_usd?: number;
  tp_price?: number;
  sl_price?: number;
  exit_plan?: string;
  rationale?: string;
  status?: 'open' | 'closed' | 'pending';
  pnl?: number;
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    if (req.method === 'POST') {
      const tradeData: TradeData = await req.json();

      const { data, error } = await supabase
        .from('trades')
        .insert([
          {
            asset: tradeData.asset,
            action: tradeData.action,
            entry_price: tradeData.entry_price,
            amount: tradeData.amount,
            allocation_usd: tradeData.allocation_usd || 0,
            tp_price: tradeData.tp_price,
            sl_price: tradeData.sl_price,
            exit_plan: tradeData.exit_plan || '',
            rationale: tradeData.rationale || '',
            status: tradeData.status || 'pending',
            pnl: tradeData.pnl,
          },
        ])
        .select()
        .single();

      if (error) {
        throw error;
      }

      return new Response(
        JSON.stringify({ success: true, data }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    if (req.method === 'PUT') {
      const { id, ...updateData } = await req.json();

      const { data, error } = await supabase
        .from('trades')
        .update(updateData)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        throw error;
      }

      return new Response(
        JSON.stringify({ success: true, data }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      {
        status: 405,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        },
      }
    );
  }
});