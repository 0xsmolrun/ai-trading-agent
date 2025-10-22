import { createClient } from 'npm:@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
};

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

    const url = new URL(req.url);
    const action = url.searchParams.get('action');

    if (action === 'status') {
      const { data: config } = await supabase
        .from('agent_config')
        .select('*')
        .limit(1)
        .maybeSingle();

      return new Response(
        JSON.stringify({ status: config?.is_active ? 'running' : 'stopped', config }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    if (action === 'start' && req.method === 'POST') {
      await supabase
        .from('agent_config')
        .update({ is_active: true })
        .eq('id', (await supabase.from('agent_config').select('id').limit(1).single()).data?.id);

      return new Response(
        JSON.stringify({ status: 'running', message: 'Agent started' }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    if (action === 'stop' && req.method === 'POST') {
      await supabase
        .from('agent_config')
        .update({ is_active: false })
        .eq('id', (await supabase.from('agent_config').select('id').limit(1).single()).data?.id);

      return new Response(
        JSON.stringify({ status: 'stopped', message: 'Agent stopped' }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    return new Response(
      JSON.stringify({ error: 'Invalid action' }),
      {
        status: 400,
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