# Nocturne Trading Agent - Web Application

This is the web dashboard for the Nocturne AI Trading Agent. The application has been converted from a Python CLI tool to a modern web application with real-time monitoring and control capabilities.

## Features

- **Real-time Dashboard**: Monitor trading performance, positions, and metrics in real-time
- **Trade History**: View detailed history of all trades with entry/exit prices, PnL, and rationale
- **Performance Metrics**: Track total return, Sharpe ratio, account value, and available cash
- **Agent Controls**: Start and stop the trading agent directly from the web interface
- **Visual Charts**: Interactive performance charts showing trading activity over time
- **Position Management**: View open positions with their current status and PnL

## Technology Stack

- **Frontend**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS 4
- **Database**: Supabase (PostgreSQL)
- **Backend**: Supabase Edge Functions (Deno)
- **Charts**: Recharts
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Supabase account (already configured)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Environment variables are already configured in `.env`:
```
VITE_SUPABASE_URL=<your-supabase-url>
VITE_SUPABASE_SUPABASE_ANON_KEY=<your-supabase-anon-key>
```

### Development

Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

Build the application for production:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Architecture

### Frontend Components

- **App.tsx**: Main application component with state management
- **Dashboard.tsx**: Main dashboard layout with stats cards
- **Controls.tsx**: Agent control panel (start/stop buttons)
- **PerformanceChart.tsx**: Line chart showing performance over time
- **PositionsPanel.tsx**: Current open positions display
- **TradesList.tsx**: Detailed table of all trades

### Database Schema

The application uses three main tables:

1. **trades**: Stores all trading activity
   - Asset, action, entry/exit prices
   - Take profit/stop loss levels
   - Rationale and exit plans
   - Status and PnL

2. **performance_metrics**: Stores performance snapshots
   - Total return percentage
   - Sharpe ratio
   - Account value
   - Available cash

3. **agent_config**: Stores agent configuration
   - Trading assets
   - Interval settings
   - Active/inactive status

### Edge Functions

1. **trading-agent**: Controls agent status (start/stop)
2. **record-trade**: Records trades to the database

## Usage

1. **Start the Agent**: Click the "Start" button to activate trading
2. **Monitor Performance**: View real-time updates on the dashboard
3. **Check Trades**: Scroll down to see detailed trade history
4. **Stop the Agent**: Click "Stop" to pause trading activity

## Differences from Python Version

The web application provides the same core functionality as the Python CLI version, but with these key differences:

- **No Python Required**: Runs entirely in the browser
- **Real-time Updates**: Dashboard updates automatically every 5 seconds
- **Visual Interface**: Beautiful, modern UI instead of CLI logs
- **Remote Control**: Start/stop trading from anywhere
- **Database Persistence**: All data stored in Supabase
- **Serverless Backend**: Uses edge functions instead of Python scripts

## Notes

- The Python trading logic still needs to be integrated with the edge functions for full automation
- Currently, the web app provides monitoring and control interface
- Sample data has been added to demonstrate the UI
- You can manually add trades via the Supabase dashboard or API

## Future Enhancements

- Full Python logic migration to TypeScript/Deno edge functions
- Real-time WebSocket updates for instant trade notifications
- Advanced charting with multiple timeframes
- Trade alerts and notifications
- Mobile-responsive design improvements
- Settings panel for configuring assets and intervals
- Export trade history to CSV
