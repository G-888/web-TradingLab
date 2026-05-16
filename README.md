# XAUUSD Gold AI — Institutional Research & Execution Framework

A professional-grade Telegram bot for quantitative XAUUSD (Gold) research, signal generation, backtesting, and edge monitoring. Built for traders who require institutional-quality analytics without institutional-level infrastructure costs.

---

## Overview

**[Dashboard Guide & Architecture](docs/DASHBOARD_GUIDE.md)**: A comprehensive manual for running and using the Next.js dashboard, including Strategy Lab details and safety boundaries.

This system combines real-time market data, multi-strategy signal generation, and a self-evaluating analytics platform into a single Telegram-based terminal. All metrics are Python-computed from live market data. AI (Groq) is used exclusively to explain outputs, not to generate them.

**Core design principles:**
- No lookahead bias in any backtest or signal
- Python computes all metrics — AI explains findings only
- No mocked data anywhere in the system
- Full SQLite persistence for all research history
- Modular architecture — every engine is independently testable

---

## Features

### 📈 Trading

| Feature | Command | Description |
|---|---|---|
| Multi-TF Analysis | `/analyze` | 1H/4H/Daily AI signal with regime context |
| Live Chart | `/chart` | 48-hour OHLCV candlestick with volume |
| Live Price | `/gold` | Spot price + TF bias snapshot |
| Fibonacci | `/fibonacci` | Swing detection, retracement levels, confluence score |
| Smart Money | `/smc` | BOS, CHoCH, order blocks, FVGs, liquidity zones |
| Sessions | `/sessions` | Live session intelligence (London/NY/Asia) |
| Confluence | `/confluence` | Multi-strategy signal alignment score |
| Voting Engine | `/votes` | 5-strategy weighted consensus signal |

### 🧠 Analytics

| Feature | Command | Description |
|---|---|---|
| Backtesting | `/backtest fib 1H 30d` | Historical strategy simulation, no lookahead |
| Performance | `/performance` | Win rate, PF, expectancy, Sharpe, vol-adj score |
| Leaderboard | `/leaderboard` | 5-dimension strategy ranking (0–100 score) |
| Diagnostics | `/diagnostics` | Overfitting, regime failure, confidence drift detection |
| Optimization | `/optimize fib 1H 30d` | Parameter grid search with robustness scoring |
| Heatmap | `/heatmap` | Multi-TF signal alignment heatmap |
| Session Analytics | `/session` | Win rate by London/NY/Asia/Overlap session |

### 📚 Research

| Feature | Command | Description |
|---|---|---|
| Decay Monitor | `/decay` | 7d/30d/90d rolling edge deterioration detection |
| Edge Health | `/edge` | Composite edge health score (0–100) per strategy |
| Regime Health | `/regimehealth` | Strategy performance across trending/ranging/volatile regimes |
| Stability | `/stability` | Consistency, confidence calibration, stability rankings |
| Strategy Compare | `/compare fib smc` | Side-by-side metric comparison with visual chart |
| Monitor | `/monitor` | System status and manual snapshot trigger |

### ⚙️ System

| Feature | Command | Description |
|---|---|---|
| Price Alerts | `/alert above 3300` | Threshold-based Telegram price alerts |
| Daily Summary | `/summary 08:00` | Scheduled market recap at your chosen UTC time |
| AI Mode | Via menu | Switch between Institutional / Scalper / Swing / Macro personas |
| Settings | Via menu | Configure all preferences |

---

## Architecture

```
xauusd-gold-ai/
│
├── main.py                    # Entry point, command registration, scheduler
│
├── market/
│   ├── data.py                # yfinance data fetching, OHLCV, live price
│   └── regime.py              # Market regime detection (trending/ranging/volatile)
│
├── strategies/
│   ├── registry.py            # Centralized list of 21 strategies (planned & implemented)
│   ├── strategy_router.py     # Safe execution routing mapping to active modules
│   ├── fibonacci.py           # Swing detection, Fibonacci levels, confluence scoring
│   ├── smc.py                 # BOS, CHoCH, order blocks, FVGs, liquidity
│   ├── session.py             # Session analysis (London/NY/Asia ranges and bias)
│   └── momentum.py            # RSI, MACD, momentum indicators
│
├── signals/
│   ├── confluence.py          # Multi-strategy alignment scoring
│   ├── voting.py              # 5-strategy weighted voting engine
│   └── heatmap.py             # Multi-timeframe signal heatmap
│
├── analytics/
│   ├── performance.py         # Core stats engine: WR, PF, expectancy, Sharpe
│   ├── leaderboard.py         # 5-dimension strategy ranking system
│   ├── diagnostics.py         # Overfitting, decay, regime failure detection
│   ├── optimizer.py           # Parameter grid search and robustness scoring
│   ├── decay.py               # 7d/30d/90d rolling edge deterioration engine
│   ├── monitoring.py          # Daily snapshot and decay check scheduler jobs
│   ├── alerts.py              # Telegram alert dispatcher for edge events
│   └── session_analytics.py   # Session-based performance breakdown
│
├── backtesting/
│   ├── engine.py              # Backtest runner, trade simulation
│   ├── metrics.py             # Metrics computation (no lookahead)
│   ├── replay.py              # Historical bar replay engine
│   └── reports.py             # Chart generation for backtest results
│
├── charts/
│   └── chart_generator.py     # All chart generation (dark institutional theme)
│
├── ai/
│   ├── ai_router.py           # Groq API client with retry and caching
│   ├── prompts.py             # Strategy-specific prompt builders
│   └── cache.py               # Response caching layer
│
├── bot/
│   ├── handlers/
│   │   ├── commands.py              # Core command handlers
│   │   ├── callbacks.py             # Inline keyboard router (all UI flows)
│   │   ├── institutional_commands.py # Backtest, votes, heatmap handlers
│   │   ├── analytics_commands.py    # Performance, leaderboard, diagnostics
│   │   ├── decay_commands.py        # Decay, edge, regime, stability handlers
│   │   └── session_commands.py      # Session analytics handler
│   └── keyboards/
│       └── menus.py                 # All inline keyboard builders (4-section UI)
│
└── storage/
    └── database.py            # SQLite schema, all DB operations, thread-safe
```

### Database Schema

| Table | Purpose |
|---|---|
| `conversations` | Chat history per user |
| `price_alerts` | Threshold price alerts |
| `summary_settings` | Daily summary schedules |
| `ai_mode_settings` | Per-user AI persona |
| `backtest_runs` | Backtest metadata and results |
| `backtest_trades` | Individual simulated trades |
| `signal_history` | Historical signal log |
| `optimization_runs` | Parameter optimization results |
| `performance_snapshots` | Daily snapshots for decay tracking |
| `regime_statistics` | Per-regime performance breakdown |

---

## Deployment

### Environment Variables

| Variable | Required | Where to get |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | [t.me/BotFather](https://t.me/BotFather) → `/newbot` |
| `GROQ_API_KEY` | Yes | [console.groq.com](https://console.groq.com) → API Keys |

**Never commit these to version control.**

---

### Option 1 — Replit (Recommended)

1. Fork or import this repository into [replit.com](https://replit.com)
2. Open **Secrets** (padlock icon in sidebar)
3. Add `TELEGRAM_BOT_TOKEN` and `GROQ_API_KEY` as secrets
4. Click **Run** or start the `Start application` workflow
5. The bot will start polling automatically
6. For persistent 24/7 uptime, use **Replit Deployments** (Autoscale or Reserved VM)

> **Note:** Free Replit instances sleep after inactivity. Use Deployments for production.

---

### Option 2 — Local (Windows)

```powershell
# 1. Install Python 3.11+ from python.org

# 2. Clone
git clone https://github.com/youruser/xauusd-gold-ai
cd xauusd-gold-ai

# 3. Create venv
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variables
set TELEGRAM_BOT_TOKEN=your_token_here
set GROQ_API_KEY=your_key_here

# 6. Run
python main.py
```

---

### Option 3 — Local (Linux / macOS)

```bash
git clone https://github.com/youruser/xauusd-gold-ai
cd xauusd-gold-ai

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export TELEGRAM_BOT_TOKEN="your_token"
export GROQ_API_KEY="your_key"

python main.py
```

---

### Option 4 — Ubuntu VPS (Production)

```bash
# 1. System setup
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y

# 2. Clone
git clone https://github.com/youruser/xauusd-gold-ai /opt/goldbot
cd /opt/goldbot

# 3. Venv + install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Secrets file
cat > /opt/goldbot/.env << EOF
TELEGRAM_BOT_TOKEN=your_token_here
GROQ_API_KEY=your_key_here
EOF
chmod 600 /opt/goldbot/.env

# 5. Systemd service
sudo tee /etc/systemd/system/goldbot.service << EOF
[Unit]
Description=XAUUSD Gold AI Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/goldbot
EnvironmentFile=/opt/goldbot/.env
ExecStart=/opt/goldbot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable goldbot
sudo systemctl start goldbot

# Check logs
sudo journalctl -u goldbot -f
```

---

### Option 5 — Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

Create `docker-compose.yml`:

```yaml
version: "3.9"
services:
  goldbot:
    build: .
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
```

```bash
# Build and run
docker compose up -d

# Logs
docker compose logs -f

# Restart
docker compose restart
```

---

### Local Web Dashboard Development

The project includes a standalone web dashboard (FastAPI backend + Next.js frontend) for monitoring the bot's data locally without executing live trades or interfering with the bot's Telegram polling.

1. Install backend dependencies:
```bash
pip install -r requirements.txt
```

2. Create local environment:
```bash
cp .env.example .env
```

3. Set environment variables in `.env`:
```
DB_PATH=data/local_dashboard_gold_bot.db
DASHBOARD_API_KEY=local-dev-key
```

4. Run dashboard API:
```bash
uvicorn dashboard_api.app:app --host 127.0.0.1 --port 8000
```

5. Run web dashboard:
```bash
cd web_dashboard
npm install
cp .env.local.example .env.local
npm run dev
```

6. Open the dashboard:
http://localhost:3000

Also, the existing Telegram bot can be started separately:
```bash
python main.py
```

**Note**: 
- Telegram bot and dashboard API run separately.
- The dashboard is **read-only**.
- The dashboard does not execute trades or start Telegram polling.

---

## Bot Operation Guide

### 4-Section Navigation

```
┌─────────────────────────────────┐
│  XAUUSD Gold AI Terminal        │
└─────────────────────────────────┘

[ 📈 Trading ]    [ 🧠 Analytics ]
[ 📚 Research ]   [ ⚙️ System    ]
```

Every screen includes **🔄 Refresh**, **🔙 Back**, and **🏠 Home** navigation.
The entire bot is operable via buttons — slash commands are optional.

### 📈 Trading submenu

| Button | Action |
|---|---|
| 📊 Analyze | Multi-TF AI signal |
| 📈 Chart | 48h candlestick |
| 📐 Fibonacci | TF → analysis |
| 🏦 Smart Money | TF → SMC analysis |
| 🕐 Sessions | Live session intelligence |
| ◆ Confluence | Signal alignment score |
| 🗳 Voting | 5-strategy consensus |
| 💰 Live Price | Spot price snapshot |

### 🧠 Analytics submenu

| Button | Action |
|---|---|
| 📊 Backtest | Strategy → TF → Range → Results |
| 📈 Performance | Full dashboard |
| 🩺 Diagnostics | Health flags |
| 🌡 Heatmap | Multi-TF alignment |
| 📉 Decay | Edge deterioration |
| 🏆 Leaderboard | Ranked strategies |
| ⚙️ Optimize | Parameter grid search |
| 🕐 Sessions | Session-based analytics |

### 📚 Research submenu

| Button | Action |
|---|---|
| 🕸 Regime Health | Regime performance radar |
| 🔬 Edge Health | Composite edge scores |
| 📊 Stability | Consistency rankings |
| ⚖️ Compare | Strategy A vs B |
| 📋 Weekly Report | Combined research digest |
| 📡 Monitor | System status |

### ⚙️ System submenu

| Button | Action |
|---|---|
| 🔔 Alerts | Set/view price alerts |
| 📰 Summary | Schedule daily recap |
| 🤖 AI Mode | Switch persona |
| ⚙️ Settings | All preferences |
| ❓ Help | Full command list |

---

## Backtesting Guide

### How backtests work

1. Data is fetched for the requested period and timeframe using yfinance
2. The bar replay engine processes bars one at a time, left to right
3. Signals are generated using only data available at that point in time
4. Entries execute on the next bar's open after signal generation
5. Exits use stop-loss and take-profit levels defined at entry
6. All trades are stored in `backtest_trades` with session and regime tags

### No Lookahead Bias

The replay engine enforces strict time ordering. No future bar data is ever available to the signal generator during a simulation. This is enforced at the architectural level, not just by convention.

### Interpreting Results

| Metric | What It Tells You |
|---|---|
| Win Rate | % of trades closed in profit |
| Profit Factor | Total wins / total losses — must be > 1.0 |
| Expectancy | Average expected points per trade |
| Max Drawdown | Worst peak-to-trough during the period |
| Avg RR | Average actual risk-reward achieved |
| Trade Count | Too few (<30) makes results unreliable |

---

## Analytics Guide

### Key Metrics

| Metric | Good Range | Concern |
|---|---|---|
| Win Rate | > 50% | < 40% = weak edge |
| Profit Factor | > 1.5 | < 1.0 = loss-making |
| Expectancy | > 0 | < 0 = negative edge |
| Sharpe | > 1.0 | < 0.5 = poor risk-adj |
| Max Drawdown | < 25% | > 40% = too risky |
| Edge Health | > 65 | < 40 = critical |
| Stability | > 60% | < 40% = fragile |

### Edge Health Grades

| Score | Grade | Action |
|---|---|---|
| 90–100 | Institutional Grade | Full confidence |
| 75–89 | Strong Edge | Trade with standard sizing |
| 60–74 | Degrading | Reduce position size |
| 40–59 | Weak Edge | Avoid trading, investigate |
| 0–39 | Critical Failure | Stop trading, re-evaluate |

### Decay Monitoring

The decay engine compares rolling 7-day, 30-day, and 90-day performance windows. When recent performance diverges significantly from historical norms, alerts are raised automatically through the daily monitoring scheduler.

---

## Strategy Lab & Benchmarking

The **Strategy Lab** is a robust environment designed to systematically backtest, forward test, compare, and rank all available strategies. It strictly acts as a sandbox testability layer without executing live trades or integrating with broker APIs.

### Key Features
1. **Batch Backtesting**: Simultaneously evaluate every implemented strategy on historical data.
2. **Paper Forward Testing**: Initialize virtual observation sessions to track live strategy performance on real market data.
3. **SMC Component Integration**: High-fidelity detection of Smart Money Concepts (BOS, CHoCH, FVG, Liquidity Sweeps).
4. **Transparent Scoring Formula**: Strategies are ranked according to a rigid, transparent score:
   `score = (win_rate * 100) + (profit_factor * 10) - (abs(max_drawdown) * 2) + (expectancy * 50) + (min(total_trades, 100) * 0.1)`

### Testability Constraints
- **Planned Strategies**: Automatically excluded from the Strategy Lab. They must be fully implemented to participate in batch testing.
- **Safety First**: The lab strictly enforces `BACKTEST ONLY` and `PAPER TEST ONLY` protocols. Backtest performance does not guarantee future results.

For a detailed technical overview, see the **[Dashboard Guide & Architecture](docs/DASHBOARD_GUIDE.md)**.

---

## Strategy Detail & Conversion Workflow

The **Strategy Registry** (`strategies/registry.py`) holds metadata for all active and planned strategies. Our Next.js dashboard uses this to provide a comprehensive roadmap and conversion workflow.

### Detail Metadata Meaning
- **how_it_works**: Core algorithm logic summary.
- **best/weak_conditions**: Environments where the strategy thrives or fails.
- **required_indicators & data**: Dependencies needed to run it.
- **readiness**: Boolean flags for `analysis`, `backtesting`, `forward_testing`, and `ea_ready`.
- **implementation_steps**: The roadmap checklist needed to build the strategy.

### How to Implement a Planned Strategy

To convert a strategy from `planned` to `implemented`:

1. **Add logic**: Create or update the strategy's `.py` file under `strategies/` (e.g. `strategies/support_resistance.py`).
2. **Standard Output**: Ensure your function returns a standard dictionary (e.g., `{"direction": "BULLISH", "confidence": 80, "reason": "..."}`).
3. **Map Function**: Open `strategies/strategy_router.py` and map your function inside `run_strategy()`.
4. **Update Registry**: In `strategies/registry.py`, change the status from `"planned"` to `"partial"` (if it's partially working) or `"implemented"`. Update `readiness["analysis"] = True`.
5. **Backtest Adapter**: Once the logic is sound, add backtest hooks. Update `readiness["backtesting"] = True`.
6. **Validation**: Complete the `validation_checklist` defined in the registry.
7. **Test Dashboard**: Open the web dashboard and verify the "Analyze" button now works without producing fake results.

> [!WARNING]
> Do NOT mark a strategy as `implemented` unless the logic exists and returns real calculations. Fake results or hardcoded signals compromise the integrity of the institutional-grade framework.

---

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Bot not responding | Wrong token | Verify `TELEGRAM_BOT_TOKEN` |
| 409 Conflict on startup | Old instance alive | Wait 30–60 seconds |
| Groq API errors | Rate limit or bad key | Check console.groq.com |
| yfinance empty data | Market closed | Retry during market hours |
| Chart not sending | Matplotlib config | Ensure `Agg` backend in chart files |
| SQLite locked | Concurrent writes | Lock is handled automatically |
| Empty backtest | Too few candles | Use longer lookback period |
| Replit sleeps | Free tier | Use Replit Deployments |

---

## Security

- Store all secrets in environment variables — never in source code
- Add `.env` and `*.db` to `.gitignore`
- Keep your bot token private — it grants full bot control to anyone who has it
- For VPS deployments, use `chmod 600` on your `.env` file
- Consider keeping the repository private if deploying with sensitive configuration

**Recommended `.gitignore` additions:**
```
.env
*.db
*.sqlite3
__pycache__/
venv/
.pythonlibs/
attached_assets/
```

---

## Disclaimer

This software is provided **for educational and research purposes only**.

- This is NOT financial advice
- Past backtest performance does NOT guarantee future results
- Do NOT use outputs from this system to make real trading decisions without independent verification
- The authors accept no liability for any trading losses

---

## License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is provided to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

---

## Roadmap

- [ ] Multi-asset support (Silver, Oil, indices)
- [ ] Live trade journaling with outcome tracking
- [ ] Walk-forward optimization validation
- [ ] Portfolio-level drawdown management
- [ ] Webhook mode for production deployments
- [ ] Strategy correlation matrix
- [x] Web dashboard (FastAPI + React/Next.js)

---

## Production Deployment Guide

To deploy the Telegram Bot and the Dashboard API/Frontend to a production server (Linux VPS recommended), follow this guide.

### 1. Environment Configurations
Do not commit your `.env` files.

**Root `.env` (Telegram & API)**
```
TELEGRAM_BOT_TOKEN=your_live_token
GROQ_API_KEY=your_live_key
DB_PATH=data/gold_bot.db
DASHBOARD_API_KEY=your_super_secret_long_key_here
DASHBOARD_ALLOWED_ORIGINS=https://dashboard.mydomain.com
```

**Frontend `web_dashboard/.env.local`**
```
NEXT_PUBLIC_API_BASE_URL=https://dashboard.mydomain.com
NEXT_PUBLIC_DASHBOARD_API_KEY=your_super_secret_long_key_here
```
> **Note:** The `NEXT_PUBLIC_DASHBOARD_API_KEY` is visible to the client browser. For maximum security in production, you should protect the dashboard via **Cloudflare Access**, **Nginx Basic Auth**, or a VPN, as the frontend strictly queries your database read-only.

### 2. Linux Systemd Setup (Recommended)
This approach keeps all processes running reliably in the background, restarting automatically on failure.

#### A. Telegram Bot (`/etc/systemd/system/telegram-bot.service`)
```ini
[Unit]
Description=AI Trading Telegram Bot
After=network.target

[Service]
User=your_linux_user
WorkingDirectory=/path/to/xauusd-gold-ai
ExecStart=/path/to/xauusd-gold-ai/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### B. Dashboard API (`/etc/systemd/system/dashboard-api.service`)
```ini
[Unit]
Description=Dashboard FastAPI Backend
After=network.target

[Service]
User=your_linux_user
WorkingDirectory=/path/to/xauusd-gold-ai
ExecStart=/path/to/xauusd-gold-ai/venv/bin/python -m uvicorn dashboard_api.app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### C. Dashboard Frontend (`/etc/systemd/system/dashboard-frontend.service`)
First, build the project:
```bash
cd web_dashboard
npm install
npm run build
```

Then create the service:
```ini
[Unit]
Description=Next.js Dashboard Frontend
After=network.target

[Service]
User=your_linux_user
WorkingDirectory=/path/to/xauusd-gold-ai/web_dashboard
Environment="PORT=3000"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Enable and Start Services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot dashboard-api dashboard-frontend
sudo systemctl start telegram-bot dashboard-api dashboard-frontend
```

### 3. Windows Server Deployment
If using Windows Server, you can use **NSSM** (Non-Sucking Service Manager) to wrap the scripts into Windows Services.

1. Download NSSM and run `nssm install TelegramBot`.
2. Set the Path to `python.exe` inside your `venv`.
3. Set Arguments to `main.py` and set the Working Directory.
4. Repeat for **Dashboard API** using arguments `-m uvicorn dashboard_api.app:app --host 127.0.0.1 --port 8000`.
5. Repeat for **Dashboard Frontend** using `npm.cmd` as the executable and `run start` as the arguments in the `web_dashboard` directory (make sure to `npm run build` first).

### 4. Nginx Reverse Proxy
To securely expose the dashboard on the web via HTTPS, use an Nginx reverse proxy.
Install Certbot (`sudo apt install certbot python3-certbot-nginx`) to provision SSL certificates.

`/etc/nginx/sites-available/dashboard`
```nginx
server {
    listen 80;
    server_name dashboard.mydomain.com;

    # Basic Auth Protection (Recommended)
    # auth_basic "Restricted Dashboard";
    # auth_basic_user_file /etc/nginx/.htpasswd;

    # Route frontend Next.js traffic
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Route FastAPI API requests
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Public Health Check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

### 5. Production Security Checklist
- [ ] **HTTPS Enforcement**: Do not run the dashboard on public HTTP.
- [ ] **Internal Ports**: Ports `8000` and `3000` must be blocked from the public internet using UFW/Windows Firewall. Only port `80` and `443` should be public.
- [ ] **Read-Only**: The dashboard cannot execute trades. Any API keys input into the frontend are purely to query SQLite.
- [ ] **Strong Keys**: Set `DASHBOARD_API_KEY` to a 64+ character random string.
- [ ] **Gitignore secrets**: Validate that `.env`, `.env.production`, and `*.db` are never committed to your public repository.
- [ ] **Database Constraints**: The SQLite connection leverages `PRAGMA journal_mode=WAL;` and `busy_timeout=5000` to prevent the dashboard from locking the DB while the Telegram bot writes data.

### 6. Troubleshooting
- **`uvicorn not recognized`**: Ensure you activated the virtual environment (`source venv/bin/activate`) before installing packages, or use the absolute path to `venv/bin/uvicorn`.
- **Database Locked**: If the frontend hangs on load, the SQLite DB is busy. Ensure `WAL` mode is active, or wait 5 seconds for the retry loop.
- **CORS Error**: Ensure the frontend domain (`https://dashboard.mydomain.com`) exactly matches `DASHBOARD_ALLOWED_ORIGINS` in your backend `.env` file.
- **Frontend Empty/Unauthorized**: Ensure the API keys match between the Next.js `.env.local` and backend `.env`. Check the Next.js `npm run start` terminal logs.
