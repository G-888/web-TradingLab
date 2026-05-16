"""
strategies/registry.py — Centralized strategy definition registry.

This file acts as the single source of truth for strategy metadata in the dashboard and backend.
It does NOT execute logic. Execution routing happens in strategy_router.py.
"""

STRATEGY_REGISTRY = {
    "fibonacci_retracement": {
        "id": "fibonacci_retracement",
        "name": "Fibonacci Retracement",
        "category": "price_action",
        "description": "Uses Fibonacci retracement levels such as 38.2%, 50%, and 61.8% to identify potential pullback entry zones.",
        "status": "implemented",
        "complexity": "medium",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["trending", "pullback", "swing"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["retracement", "support_resistance", "price_action"],
        "notes": "Works better when combined with structure, liquidity, and trend confirmation.",
        "how_it_works": "Automatically detects the most recent significant swing high and low, calculates key Fibonacci levels (23.6%, 38.2%, 50%, 61.8%, 78.6%), and scores confluence based on proximity, RSI alignment, and ATR.",
        "best_conditions": ["Clear trending market", "Moderate volatility", "Post-impulsive moves"],
        "weak_conditions": ["Chop/Ranging market", "Low volatility", "Pre-news consolidation"],
        "required_indicators": ["Swing High/Low Detector", "RSI", "ATR"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Detect swing highs/lows dynamically",
            "Calculate Fibonacci retracement and extension levels",
            "Identify nearest level to current price",
            "Score confluence with RSI and ATR",
            "Determine bullish/bearish bias",
            "Expose analysis to FastAPI router"
        ],
        "readiness": {
            "analysis": True,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Can produce false signals in ranging markets", "Subjective if swing points are not strictly defined programmatically"],
        "validation_checklist": ["Swing detection handles edge cases", "Confluence score normalizes to 0-100", "Tested in H1 and H4"],
        "recommended_priority": "high"
    },
    "smart_money_concepts": {
        "id": "smart_money_concepts",
        "name": "Smart Money Concepts",
        "category": "smc",
        "description": "Uses market structure, liquidity sweeps, order blocks, imbalance, and break of structure.",
        "status": "implemented",
        "complexity": "high",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "GBPJPY", "NQ100"],
        "market_regimes": ["trending", "liquidity-driven", "volatile"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["smc", "liquidity", "order_block"],
        "notes": "Advanced institutional trading concepts.",
        "how_it_works": "Analyzes price action to detect Institutional order flow footprints: Breaks of Structure (BOS), Change of Character (CHoCH), Order Blocks (OB), Fair Value Gaps (FVG), and Liquidity Sweeps.",
        "best_conditions": ["High liquidity periods (London/NY overlap)", "Trending markets with clear pullbacks", "Post-liquidity sweeps"],
        "weak_conditions": ["Asian session slow drift", "Low volume holidays"],
        "required_indicators": ["Market Structure Engine", "Fractal Highs/Lows", "Volume Profile (Optional)"],
        "required_data": ["OHLC candles", "Tick volume (if available)"],
        "implementation_steps": [
            "Build BOS and CHoCH detection",
            "Identify unmitigated Order Blocks",
            "Detect Fair Value Gaps (FVG)",
            "Identify liquidity sweep patterns",
            "Determine overall directional bias",
            "Map to FastAPI router"
        ],
        "readiness": {
            "analysis": True,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Highly complex programmatic definitions", "Prone to repainting if structure rules aren't strict"],
        "validation_checklist": ["BOS/CHoCH do not repaint", "Order blocks are invalidated upon mitigation", "FVG fills are tracked correctly"],
        "recommended_priority": "high"
    },
    "elliott_wave": {
        "id": "elliott_wave",
        "name": "Elliott Wave",
        "category": "wave_analysis",
        "description": "Uses impulse and corrective wave structures to identify possible continuation or reversal zones.",
        "status": "planned",
        "complexity": "high",
        "supported_timeframes": ["H1", "H4", "D1"],
        "recommended_symbols": ["NQ100", "XAUUSD", "EURUSD"],
        "market_regimes": ["trending", "swing"],
        "risk_level": "high",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["wave_analysis", "swing_trading"],
        "notes": "Subjective; should be treated as assisted analysis, not fully automated certainty.",
        "how_it_works": "Attempts to map market cycles into 5-wave motive sequences and 3-wave corrective sequences using fractal geometry.",
        "best_conditions": ["Macro trending environments", "High timeframe analysis (D1/H4)"],
        "weak_conditions": ["Intraday chop", "News-driven volatility spikes"],
        "required_indicators": ["ZigZag", "Fibonacci Extensions", "Fractal Detector"],
        "required_data": ["OHLC candles", "Multi-timeframe historical context"],
        "implementation_steps": [
            "Build high-timeframe ZigZag / Swing detector",
            "Identify candidate impulse waves (1, 3, 5)",
            "Identify candidate corrective waves (A, B, C)",
            "Enforce Elliott Wave invalidation rules (e.g., Wave 4 cannot overlap Wave 1)",
            "Build AI-assisted interpretation module",
            "Expose manual-assisted roadmap UI"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Highly subjective", "Extremely difficult to programmatically validate without false positives", "Requires human-in-the-loop assistance"],
        "validation_checklist": ["Wave 3 is never the shortest", "Wave 2 never retraces >100% of Wave 1", "Wave 4 does not enter Wave 1 territory"],
        "recommended_priority": "low"
    },
    "support_resistance": {
        "id": "support_resistance",
        "name": "Support and Resistance",
        "category": "price_action",
        "description": "Identifies horizontal reaction zones based on prior highs/lows and price reactions.",
        "status": "planned",
        "complexity": "low",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["ranging", "swing"],
        "risk_level": "low",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["support_resistance", "price_action"],
        "notes": "Core foundation for most other strategies.",
        "how_it_works": "Scans historical data for price clusters, swing points, and repeated rejection levels to draw horizontal zones of supply (resistance) and demand (support).",
        "best_conditions": ["Ranging markets", "Consolidation phases", "Swing trading"],
        "weak_conditions": ["Parabolic trends", "Price discovery mode (All Time Highs)"],
        "required_indicators": ["Swing High/Low", "Volume Profile (Optional)", "Price Clustering Algorithm"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Add swing high/low detector",
            "Cluster nearby swing levels into 'zones'",
            "Score zone strength by number of historical touches and rejections",
            "Add breakout/retest validation logic",
            "Add invalidation rules (zone broken)",
            "Standardize output format",
            "Add backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Zones can be subjective depending on cluster tolerance", "Fakeouts are common without volume confirmation"],
        "validation_checklist": ["Clustering algorithm does not create redundant zones", "Strength score accurately reflects historical respect"],
        "recommended_priority": "high"
    },
    "trend_following": {
        "id": "trend_following",
        "name": "Trend Following",
        "category": "trend",
        "description": "Follows established trends using moving averages, higher highs/lows, and trend strength.",
        "status": "planned",
        "complexity": "low",
        "supported_timeframes": ["H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["trending"],
        "risk_level": "low",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["trend", "momentum"],
        "notes": "Simple higher-timeframe alignment.",
        "how_it_works": "Uses a combination of Moving Averages (e.g., 50 EMA / 200 EMA) and ADX to determine trend direction and strength, taking trades only in the direction of the dominant trend.",
        "best_conditions": ["Strong trending markets", "Macro economic shifts"],
        "weak_conditions": ["Ranging markets", "Whipsaw environments"],
        "required_indicators": ["EMA", "SMA", "ADX"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Implement EMA/SMA calculations",
            "Implement ADX for trend strength",
            "Create alignment logic (e.g., Price > 50 EMA > 200 EMA)",
            "Define entry triggers (e.g., pullback to 50 EMA)",
            "Define trailing stop logic"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Severe drawdown during extended ranging periods", "Late entries if moving averages are too slow"],
        "validation_checklist": ["Filters out trades when ADX < 20", "Moving average calculations are accurate"],
        "recommended_priority": "medium"
    },
    "moving_average_crossover": {
        "id": "moving_average_crossover",
        "name": "Moving Average Crossover",
        "category": "trend",
        "description": "Uses fast and slow moving average crossovers to detect trend shifts.",
        "status": "implemented",
        "complexity": "low",
        "supported_timeframes": ["H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["trending"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["trend", "moving_average"],
        "notes": "Can be susceptible to false signals in ranging markets.",
        "how_it_works": "Generates a BUY signal when a fast moving average crosses above a slow moving average, and a SELL signal when it crosses below.",
        "best_conditions": ["Trending environments", "High timeframe analysis"],
        "weak_conditions": ["Ranging markets (causes whipsaws)", "Low volatility"],
        "required_indicators": ["EMA fast", "EMA slow"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Calculate fast and slow MAs",
            "Detect crossover events",
            "Add volume or RSI filter to reduce whipsaws",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": True,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Lagging indicator", "High frequency of false signals in chop"],
        "validation_checklist": ["Crossover events trigger on exactly the close of the crossing candle"],
        "recommended_priority": "medium"
    },
    "rsi_mean_reversion": {
        "id": "rsi_mean_reversion",
        "name": "RSI Mean Reversion",
        "category": "mean_reversion",
        "description": "Uses RSI overbought/oversold conditions with confirmation to identify mean reversion opportunities.",
        "status": "implemented",
        "complexity": "low",
        "supported_timeframes": ["M5", "M15", "M30", "H1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["ranging"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["rsi", "mean_reversion", "oscillator"],
        "notes": "Best traded within established support and resistance bounds.",
        "how_it_works": "Looks for RSI readings above 70 or below 30, coupled with price action rejection patterns, to trade a return to the mean.",
        "best_conditions": ["Ranging markets", "Established channels"],
        "weak_conditions": ["Strong trending markets (RSI can stay overbought for a long time)"],
        "required_indicators": ["RSI", "Bollinger Bands (Optional)"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Implement RSI calculation",
            "Define dynamic overbought/oversold thresholds",
            "Add price action confirmation (e.g. pin bar)",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Dangerous to counter-trade strong trends blindly"],
        "validation_checklist": ["Requires confirmation candle before entry, not just RSI touch"],
        "recommended_priority": "medium"
    },
    "macd_momentum": {
        "id": "macd_momentum",
        "name": "MACD Momentum",
        "category": "momentum",
        "description": "Uses MACD line, signal line, and histogram momentum confirmation.",
        "status": "planned",
        "complexity": "low",
        "supported_timeframes": ["M30", "H1", "H4"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["trending", "momentum"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["macd", "momentum", "oscillator"],
        "notes": "Often used for divergence spotting.",
        "how_it_works": "Analyzes the MACD histogram and signal line crossovers to capture momentum bursts, heavily utilizing bullish/bearish divergences.",
        "best_conditions": ["Start of new trends", "High momentum periods"],
        "weak_conditions": ["Low volatility ranges"],
        "required_indicators": ["MACD"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Implement MACD standard calculation",
            "Build divergence detection logic (Price makes Lower Low, MACD makes Higher Low)",
            "Generate signals on zero-line crosses and divergences",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Divergence detection can be complex to code programmatically without false positives"],
        "validation_checklist": ["Divergences are accurately identified across N lookback bars"],
        "recommended_priority": "medium"
    },
    "bollinger_reversion": {
        "id": "bollinger_reversion",
        "name": "Bollinger Band Mean Reversion",
        "category": "mean_reversion",
        "description": "Uses Bollinger Band extremes and return-to-mean behavior.",
        "status": "planned",
        "complexity": "medium",
        "supported_timeframes": ["M15", "M30", "H1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["ranging"],
        "risk_level": "high",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["bollinger", "volatility", "mean_reversion"],
        "notes": "Dangerous during strong trend breakouts.",
        "how_it_works": "Sells when price pierces the upper Bollinger Band and buys when it pierces the lower band, targeting the 20 SMA mean.",
        "best_conditions": ["Consolidating/Ranging markets", "Low impact news periods"],
        "weak_conditions": ["Breakouts", "Trend continuations", "High impact news (NFP, CPI)"],
        "required_indicators": ["Bollinger Bands", "RSI (Optional confirmation)"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Calculate Bollinger Bands (20, 2)",
            "Detect price closing outside bands",
            "Detect price reverting back inside bands (trigger)",
            "Set target to 20 SMA",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["'Riding the band' during trends causes severe losses"],
        "validation_checklist": ["Includes trend filter to disable trades during high ADX environments"],
        "recommended_priority": "medium"
    },
    "breakout_strategy": {
        "id": "breakout_strategy",
        "name": "Breakout Strategy",
        "category": "breakout",
        "description": "Trades breakouts above resistance or below support with volatility confirmation.",
        "status": "planned",
        "complexity": "medium",
        "supported_timeframes": ["M5", "M15", "M30"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["breakout", "volatile"],
        "risk_level": "high",
        "requires_volume": True,
        "requires_news_filter": False,
        "tags": ["breakout", "momentum"],
        "notes": "Volume confirmation is crucial.",
        "how_it_works": "Identifies periods of low volatility (consolidation) and trades the explosive expansion when price breaks the established range, using volume to confirm genuine breakouts versus fakeouts.",
        "best_conditions": ["London or NY open", "Post-consolidation phases", "High volume periods"],
        "weak_conditions": ["Asian session", "Illiquid times of day"],
        "required_indicators": ["ATR", "Support/Resistance Zones", "Volume"],
        "required_data": ["OHLC candles", "Tick volume"],
        "implementation_steps": [
            "Detect consolidation ranges",
            "Monitor volume for spike above moving average",
            "Trigger on candle close outside the range",
            "Define trailing stop logic based on ATR",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Fakeouts (liquidity sweeps) are common and trigger stop losses frequently"],
        "validation_checklist": ["Requires volume confirmation > 1.5x average", "Requires strong candle close outside zone"],
        "recommended_priority": "medium"
    },
    "liquidity_sweep": {
        "id": "liquidity_sweep",
        "name": "Liquidity Sweep",
        "category": "smc",
        "description": "Detects stop-hunt style price sweeps above highs or below lows followed by rejection.",
        "status": "planned",
        "complexity": "high",
        "supported_timeframes": ["M5", "M15", "M30", "H1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["liquidity-driven", "ranging"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["smc", "liquidity", "rejection"],
        "notes": "Wait for close back inside the range.",
        "how_it_works": "Identifies when price pierces a significant high/low but fails to close beyond it (leaving a wick), indicating smart money triggered stops and is reversing price.",
        "best_conditions": ["Session opens", "Pre-news liquidity hunts", "Established trading ranges"],
        "weak_conditions": ["Strong one-sided trends"],
        "required_indicators": ["Swing Points", "Fractals"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Identify key swing highs and lows (liquidity pools)",
            "Detect price crossing the pool but closing back inside",
            "Validate with reversal candlestick pattern (pin bar, engulfing)",
            "Set targets to opposing liquidity pools",
            "Standardize API output"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Difficult to distinguish between a sweep and a genuine breakout initially"],
        "validation_checklist": ["Ensures candle body closes back inside the structure level", "Only sweeps major swing points"],
        "recommended_priority": "high"
    },
    "order_block": {
        "id": "order_block",
        "name": "Order Block",
        "category": "smc",
        "description": "Identifies potential institutional order zones before impulsive moves.",
        "status": "planned",
        "complexity": "high",
        "supported_timeframes": ["M15", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["trending", "swing"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["smc", "order_block", "institutional"],
        "notes": "High probability zones.",
        "how_it_works": "Finds the last down-candle before a strong impulsive up-move (Bullish OB) or the last up-candle before a strong down-move (Bearish OB), marking them as zones for future price mitigation.",
        "best_conditions": ["Trending markets pulling back", "Confluence with Fibonacci levels"],
        "weak_conditions": ["Ranging markets (generates too many weak blocks)"],
        "required_indicators": ["Market Structure Engine", "Volume Expansion Detector"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Identify strong impulsive price moves (imbalance)",
            "Locate the preceding opposing candle",
            "Draw zone from high to low of that candle",
            "Track mitigation (has price tapped it yet?)",
            "Standardize API output"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Not all order blocks are respected; context is everything"],
        "validation_checklist": ["Only detects OBs that caused a Break of Structure (BOS)", "Marks OBs as mitigated once touched"],
        "recommended_priority": "high"
    },
    "fair_value_gap": {
        "id": "fair_value_gap",
        "name": "Fair Value Gap",
        "category": "smc",
        "description": "Identifies price imbalance zones that may later be revisited.",
        "status": "planned",
        "complexity": "high",
        "supported_timeframes": ["M5", "M15", "H1", "H4"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["trending", "imbalance"],
        "risk_level": "low",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["smc", "fvg", "imbalance"],
        "notes": "Often used as targets or entries.",
        "how_it_works": "Locates 3-candle sequences where the high of candle 1 does not overlap with the low of candle 3 (bullish FVG), creating an area of inefficient pricing that the market seeks to fill.",
        "best_conditions": ["High momentum environments", "Post-news volatility"],
        "weak_conditions": ["Low volatility consolidation"],
        "required_indicators": ["Price Inefficiency Algorithm"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Build 3-candle pattern detector for imbalances",
            "Calculate top, bottom, and 50% consequent encroachment levels",
            "Track partial vs full mitigation of the gap",
            "Use as entry triggers or take profit targets",
            "Standardize API output"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Generates too many zones on lower timeframes", "Price doesn't always fill the FVG immediately"],
        "validation_checklist": ["FVG is invalidated once price closes through it completely", "Only flags significant FVGs > certain ATR %"],
        "recommended_priority": "high"
    },
    "supply_demand": {
        "id": "supply_demand",
        "name": "Supply and Demand",
        "category": "price_action",
        "description": "Identifies demand zones and supply zones based on strong price reactions.",
        "status": "planned",
        "complexity": "medium",
        "supported_timeframes": ["H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["ranging", "trending", "swing"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["supply_demand", "price_action", "zones"],
        "notes": "Broader zones than exact support/resistance lines.",
        "how_it_works": "Similar to Order Blocks, but focuses on broader consolidation bases before a strong rally (Demand) or strong drop (Supply), trading the first return to the base.",
        "best_conditions": ["Swing trading", "Macro timeframe analysis"],
        "weak_conditions": ["Choppy intraday price action"],
        "required_indicators": ["Base/Rally/Drop Pattern Detector"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Detect Rally-Base-Rally, Drop-Base-Drop, etc. patterns",
            "Draw zones around the 'Base' consolidation",
            "Score zone freshness (untested vs tested)",
            "Build entry logic on first return",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Defining the exact 'base' programmatically is fuzzy"],
        "validation_checklist": ["Differentiates between untested (fresh) and tested zones"],
        "recommended_priority": "medium"
    },
    "market_structure_break": {
        "id": "market_structure_break",
        "name": "Market Structure Break",
        "category": "price_action",
        "description": "Uses break of structure and change of character to identify directional bias.",
        "status": "partial",
        "complexity": "high",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["trending", "reversal"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["price_action", "structure", "choch", "bos"],
        "notes": "Essential for trend validation.",
        "how_it_works": "Tracks Higher Highs/Higher Lows for uptrends. A break below the last Higher Low indicates a Change of Character (bearish reversal warning).",
        "best_conditions": ["Reversal points", "Trending markets"],
        "weak_conditions": ["Complex corrective structures", "Ranging markets"],
        "required_indicators": ["Swing Points", "Trend Logic Algorithm"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Refine BOS/CHoCH logic currently in SMC module into a standalone analyzer",
            "Ensure candle bodies close beyond structure to confirm breaks (avoid wicks)",
            "Output clear directional bias based solely on structure",
            "Map isolated function in strategy_router"
        ],
        "readiness": {
            "analysis": True,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Wick vs Body closes can produce varying subjective results"],
        "validation_checklist": ["Only accepts body closes for valid structural breaks"],
        "recommended_priority": "high"
    },
    "session_breakout": {
        "id": "session_breakout",
        "name": "Session Breakout",
        "category": "session",
        "description": "Uses London/New York/Asia session range breakouts.",
        "status": "implemented",
        "complexity": "medium",
        "supported_timeframes": ["M5", "M15"],
        "recommended_symbols": ["GBPUSD", "GBPJPY", "EURUSD", "XAUUSD"],
        "market_regimes": ["breakout", "session-open"],
        "risk_level": "high",
        "requires_volume": True,
        "requires_news_filter": True,
        "tags": ["session", "breakout", "timing"],
        "notes": "Highly time-dependent.",
        "how_it_works": "Maps the high/low of the Asian session. When London or NY opens, it trades the breakout of that range, or fades the false breakout (London Sweep).",
        "best_conditions": ["London Open", "NY Open", "Tight Asian range compression"],
        "weak_conditions": ["Wide, volatile Asian sessions", "Mid-session lulls"],
        "required_indicators": ["Time-based Range Boxes", "ATR"],
        "required_data": ["OHLC candles", "UTC Timestamp alignment"],
        "implementation_steps": [
            "Calculate Asian session high/low",
            "Detect London open timeframe",
            "Determine breakout vs fakeout logic based on close",
            "Calculate target based on range expansion",
            "Provide analysis results via API"
        ],
        "readiness": {
            "analysis": True,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Strictly relies on accurate broker UTC timezone alignment"],
        "validation_checklist": ["Correctly handles DST shifts", "Distinguishes between a genuine breakout and a liquidity sweep"],
        "recommended_priority": "high"
    },
    "multi_timeframe_confluence": {
        "id": "multi_timeframe_confluence",
        "name": "Multi-Timeframe Confluence",
        "category": "confluence",
        "description": "Combines signals across multiple timeframes to improve confidence.",
        "status": "partial",
        "complexity": "high",
        "supported_timeframes": ["M15", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["all"],
        "risk_level": "low",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["mtf", "confluence", "alignment"],
        "notes": "Filters out false signals but reduces frequency.",
        "how_it_works": "Aggregates bias from H4 (Macro trend), H1 (Intermediate structure), and M15 (Execution entry) to ensure all timeframes agree before a signal is valid.",
        "best_conditions": ["Clear macro trends", "Patient swing trading"],
        "weak_conditions": ["Choppy markets where MTF signals conflict constantly"],
        "required_indicators": ["Cross-timeframe Data Aggregator", "Core Strategy Logic"],
        "required_data": ["OHLC candles (M15, H1, H4 simultaneously)"],
        "implementation_steps": [
            "Fetch candles for 3 separate timeframes simultaneously",
            "Run base strategy analysis on all 3",
            "Compare resulting biases",
            "Output combined confidence score",
            "Map standalone function in strategy_router"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Reduces trade frequency significantly", "Requires robust backend data fetching concurrency"],
        "validation_checklist": ["Does not suffer from lookahead bias when backtesting lower TFs against higher TFs"],
        "recommended_priority": "high"
    },
    "price_action_pattern": {
        "id": "price_action_pattern",
        "name": "Price Action Pattern",
        "category": "price_action",
        "description": "Detects patterns such as pin bar, engulfing candle, inside bar, and rejection candles.",
        "status": "planned",
        "complexity": "low",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["all"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["candlestick", "pattern", "rejection"],
        "notes": "Needs context (e.g. at a key level) to be effective.",
        "how_it_works": "Scans candlestick shapes to identify reversal patterns (Pin Bar, Bullish/Bearish Engulfing) or continuation patterns (Inside Bar) based on open/high/low/close ratios.",
        "best_conditions": ["When occurring precisely on key Support/Resistance zones"],
        "weak_conditions": ["In the middle of a range (useless noise)"],
        "required_indicators": ["Candlestick Math Logic"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Implement math for detecting wick-to-body ratios (Pin Bar)",
            "Implement logic for engulfing candles",
            "Add a 'context' requirement (must be near a key zone)",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Candlestick patterns alone have zero statistical edge without context"],
        "validation_checklist": ["Strict definitions for wick sizes to avoid false positives"],
        "recommended_priority": "low"
    },
    "volume_confirmation": {
        "id": "volume_confirmation",
        "name": "Volume Confirmation",
        "category": "volume",
        "description": "Uses volume expansion or confirmation to validate signal strength.",
        "status": "planned",
        "complexity": "medium",
        "supported_timeframes": ["M5", "M15", "M30", "H1"],
        "recommended_symbols": ["NQ100", "DJI30", "USOIL"],
        "market_regimes": ["breakout", "momentum"],
        "risk_level": "low",
        "requires_volume": True,
        "requires_news_filter": False,
        "tags": ["volume", "confirmation", "momentum"],
        "notes": "Requires reliable exchange volume data.",
        "how_it_works": "Validates price moves by ensuring that up-moves occur on increasing volume and down-moves on decreasing volume (for uptrends), or spots Volume Divergence to predict reversals.",
        "best_conditions": ["Breakouts", "Reversals"],
        "weak_conditions": ["Forex markets (where volume is decentralized tick volume)"],
        "required_indicators": ["Volume Moving Average", "OBV (On Balance Volume)"],
        "required_data": ["OHLC candles", "Real Exchange Volume"],
        "implementation_steps": [
            "Implement OBV calculation",
            "Implement Volume moving average",
            "Detect volume spikes > 2 std deviations",
            "Provide signal validation logic"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Tick volume in FX/CFDs is often unreliable compared to futures volume"],
        "validation_checklist": ["Ensure volume data is accurate for the selected symbol"],
        "recommended_priority": "medium"
    },
    "atr_volatility_strategy": {
        "id": "atr_volatility_strategy",
        "name": "ATR Volatility Strategy",
        "category": "volatility",
        "description": "Uses ATR for volatility filtering, stop loss sizing, and breakout validation.",
        "status": "planned",
        "complexity": "medium",
        "supported_timeframes": ["H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["volatile", "breakout"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["atr", "volatility", "risk_management"],
        "notes": "Excellent for dynamic risk management.",
        "how_it_works": "Uses the Average True Range to measure market volatility. Trades breakouts when a candle closes more than 1 ATR outside a consolidation, and sets dynamic stop losses (e.g. 1.5x ATR).",
        "best_conditions": ["Transitions from low volatility to high volatility"],
        "weak_conditions": ["Consistently low volatility periods"],
        "required_indicators": ["ATR", "Keltner Channels (Optional)"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Calculate 14-period ATR",
            "Build dynamic stop loss calculation logic",
            "Detect volatility contraction (squeeze)",
            "Trigger on volatility expansion",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["ATR is lagging; sudden news spikes skew it heavily"],
        "validation_checklist": ["Stop losses dynamically adjust properly without repainting past bars"],
        "recommended_priority": "high"
    },
    "ichimoku_trend": {
        "id": "ichimoku_trend",
        "name": "Ichimoku Trend Strategy",
        "category": "trend",
        "description": "Uses Ichimoku cloud, Tenkan, Kijun, and cloud structure for trend confirmation.",
        "status": "planned",
        "complexity": "high",
        "supported_timeframes": ["H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD"],
        "market_regimes": ["trending"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["ichimoku", "trend", "cloud"],
        "notes": "Works best on H4 and Daily timeframes.",
        "how_it_works": "A complete trend system. Generates signals on TK cross (Tenkan crosses Kijun), confirmed by price being above/below the Kumo (Cloud), with the Chikou Span confirming past momentum.",
        "best_conditions": ["Sustained macro trends", "High timeframe (Daily/H4)"],
        "weak_conditions": ["Ranging markets (price gets stuck inside the cloud)"],
        "required_indicators": ["Ichimoku Kinko Hyo (Tenkan, Kijun, Senkou A, Senkou B, Chikou)"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Implement all 5 Ichimoku components",
            "Define strict Kumo Breakout logic",
            "Define TK Cross logic",
            "Use cloud thickness to gauge support strength",
            "Build backtest adapter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": False,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["High complexity visualization", "Lagging system that enters late but captures safe middle-trend"],
        "validation_checklist": ["Cloud calculations project correctly 26 periods ahead"],
        "recommended_priority": "medium"
    },
    "macd_momentum": {
        "id": "macd_momentum",
        "name": "MACD Momentum",
        "category": "momentum",
        "description": "Trend-following strategy based on Moving Average Convergence Divergence crossovers.",
        "status": "implemented",
        "complexity": "low",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD", "BTCUSD", "ETHUSD", "USOIL"],
        "market_regimes": ["trending"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["macd", "momentum", "trend"],
        "notes": "Classic indicator cross strategy.",
        "how_it_works": "BUY when MACD crosses above Signal and histogram turns positive. SELL when MACD crosses below Signal and histogram turns negative.",
        "best_conditions": ["Trending markets", "Volatility expansion"],
        "weak_conditions": ["Ranging markets", "Low volatility chop"],
        "required_indicators": ["MACD", "ATR"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Calculate MACD and Signal line",
            "Calculate ATR for dynamic SL/TP",
            "Track histogram crossovers",
            "Generate signals and track trades"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Lagging indicator", "Prone to whipsaws in sideways markets"],
        "validation_checklist": ["Correct MACD calculation logic"],
        "recommended_priority": "high"
    },
    "bollinger_reversion": {
        "id": "bollinger_reversion",
        "name": "Bollinger Reversion",
        "category": "mean_reversion",
        "description": "Mean reversion strategy identifying exhaustion outside Bollinger Bands.",
        "status": "implemented",
        "complexity": "medium",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "DJI30", "GBPJPY", "USDJPY", "EURUSD"],
        "market_regimes": ["ranging", "swing"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["bollinger", "mean_reversion", "volatility"],
        "notes": "Trades fade moves outside standard deviation 2.",
        "how_it_works": "BUY when price closes below Lower Band then inside. SELL when price closes above Upper Band then inside.",
        "best_conditions": ["Ranging markets"],
        "weak_conditions": ["Strong trending markets"],
        "required_indicators": ["Bollinger Bands", "ATR"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Calculate SMA and Standard Deviation",
            "Evaluate closing relative to bands",
            "Generate signals and track trades"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["False signals in strong trends"],
        "validation_checklist": ["Correct Bollinger math"],
        "recommended_priority": "high"
    },
    "atr_volatility_strategy": {
        "id": "atr_volatility_strategy",
        "name": "ATR Volatility Breakout",
        "category": "breakout",
        "description": "Trades breakouts of a 20-candle range when ATR indicates expanding volatility.",
        "status": "implemented",
        "complexity": "low",
        "supported_timeframes": ["M15", "M30", "H1", "H4"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["breakout", "trending"],
        "risk_level": "high",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["atr", "volatility", "breakout"],
        "notes": "Best traded during session overlaps.",
        "how_it_works": "BUY when price breaks 20-candle high and ATR > ATR SMA. SELL when price breaks 20-candle low and ATR > ATR SMA.",
        "best_conditions": ["Volatility expansion", "Session opens"],
        "weak_conditions": ["Ranging chop"],
        "required_indicators": ["ATR"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Calculate ATR and ATR SMA",
            "Track rolling 20-period highs and lows",
            "Generate signals on breaks with volatility filter"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["False breakouts in low liquidity"],
        "validation_checklist": ["Correct rolling high/low tracking"],
        "recommended_priority": "high"
    },
    "support_resistance": {
        "id": "support_resistance",
        "name": "Support and Resistance",
        "category": "price_action",
        "description": "Mechanically identifies swing highs and lows, clusters them into zones, and trades rejection patterns from these levels.",
        "status": "implemented",
        "complexity": "medium",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "GBPJPY", "EURUSD"],
        "market_regimes": ["ranging", "pullback"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": False,
        "tags": ["support_resistance", "price_action", "rejection"],
        "notes": "Relies on mechanical clustering of swing points.",
        "how_it_works": "BUY when price rejects from a clustered support zone. SELL when price rejects from a clustered resistance zone.",
        "best_conditions": ["Ranging channels", "Consolidation patterns"],
        "weak_conditions": ["Strong breakouts that blow through zones"],
        "required_indicators": ["Price Action"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Detect N-period swing highs and lows",
            "Cluster nearby swings into zones using ATR tolerance",
            "Detect pin bar or rejection wicks at zones",
            "Set fixed RR targets"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Zones are subjective, mechanical approximation struggles with complex wicks"],
        "validation_checklist": ["Correct swing point clustering"],
        "recommended_priority": "high"
    },
    "liquidity_sweep": {
        "id": "liquidity_sweep",
        "name": "Liquidity Sweep (SMC)",
        "category": "smc",
        "description": "Mechanical SMC adapter trading stop hunts and liquidity sweeps above old highs and below old lows.",
        "status": "implemented",
        "complexity": "high",
        "supported_timeframes": ["M15", "M30", "H1", "H4"],
        "recommended_symbols": ["XAUUSD", "NQ100", "EURUSD", "GBPUSD"],
        "market_regimes": ["ranging", "reversal"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["smc", "liquidity", "sweep", "stop_hunt"],
        "notes": "Highly dependent on swing definition.",
        "how_it_works": "BUY when price sweeps a previous swing low and closes back inside. SELL when price sweeps a previous swing high and closes back inside.",
        "best_conditions": ["High liquidity zones", "Session opens"],
        "weak_conditions": ["Strong directional trends without pullbacks"],
        "required_indicators": ["SMC Swings"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Detect N-period swings",
            "Detect sweep wicks",
            "Place exact SL beyond sweep wick",
            "Target fixed 2.0 RR"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Mechanical definitions miss context like higher timeframe structure"],
        "validation_checklist": ["Correct sweep identification"],
        "recommended_priority": "high"
    },
    "market_structure_break": {
        "id": "market_structure_break",
        "name": "Market Structure Break (BOS)",
        "category": "smc",
        "description": "Mechanical SMC adapter trading momentum breaks of prior structural swing highs and lows.",
        "status": "implemented",
        "complexity": "medium",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "EURUSD", "GBPUSD"],
        "market_regimes": ["trending", "breakout"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["smc", "bos", "market_structure", "breakout"],
        "notes": "Aggressive entry immediately upon structural break.",
        "how_it_works": "BUY when price breaks and closes above a prior swing high. SELL when price breaks and closes below a prior swing low.",
        "best_conditions": ["Strong trending markets"],
        "weak_conditions": ["Ranging markets (creates false BOS)"],
        "required_indicators": ["SMC Swings"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Detect N-period swings",
            "Identify structural breaks (closes past prior swings)",
            "Place exact SL beyond prior swing origin",
            "Target fixed 2.0 RR"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["Aggressive entries can be prone to fakeouts in chop"],
        "validation_checklist": ["Correct BOS identification"],
        "recommended_priority": "high"
    },
    "fair_value_gap": {
        "id": "fair_value_gap",
        "name": "Fair Value Gap (FVG)",
        "category": "smc",
        "description": "Mechanical SMC adapter trading imbalances and fair value gaps.",
        "status": "implemented",
        "complexity": "medium",
        "supported_timeframes": ["M15", "M30", "H1", "H4", "D1"],
        "recommended_symbols": ["XAUUSD", "NQ100", "EURUSD", "GBPUSD"],
        "market_regimes": ["trending", "pullback"],
        "risk_level": "medium",
        "requires_volume": False,
        "requires_news_filter": True,
        "tags": ["smc", "fvg", "imbalance"],
        "notes": "Entries occur when price retraces to test the gap.",
        "how_it_works": "BUY when price retraces into a bullish FVG and closes bullish. SELL when price retraces into a bearish FVG and closes bearish.",
        "best_conditions": ["Strong impulse followed by measured pullback"],
        "weak_conditions": ["Choppy markets with overlapping candles"],
        "required_indicators": ["SMC FVG Detector"],
        "required_data": ["OHLC candles"],
        "implementation_steps": [
            "Detect 3-candle imbalance zones",
            "Monitor for price retracing into zone",
            "Wait for confirmation candle",
            "Place SL beyond the FVG",
            "Target fixed 2.0 RR"
        ],
        "readiness": {
            "analysis": False,
            "backtesting": True,
            "forward_testing": False,
            "ea_ready": False
        },
        "limitations": ["FVGs can be mitigated and ignored by the market without structure context"],
        "validation_checklist": ["Correct FVG identification and mitigation"],
        "recommended_priority": "high"
    }
}

# -- Inject Testability Layer dynamically --
for s_id, s in STRATEGY_REGISTRY.items():
    status = s.get("status", "planned")
    analysis_ready = s.get("readiness", {}).get("analysis", False)
    
    can_analyze = (status == "implemented") or (status == "partial" and analysis_ready)
    can_backtest = (s_id in ["moving_average_crossover", "rsi_mean_reversion", "macd_momentum", "bollinger_reversion", "atr_volatility_strategy", "support_resistance", "fibonacci_retracement", "liquidity_sweep", "market_structure_break", "fair_value_gap"]) # Enabled for tested strategies
    can_forward_test = can_backtest # Enabled for forward testing
    
    reason = "Ready for analysis." if can_analyze else "Not testable."
    if status == "planned":
        reason = "Planned strategy. Implementation required."
    if can_backtest:
        reason += " Backtest adapter available."
        
    s["testability"] = {
        "can_analyze": can_analyze,
        "can_backtest": can_backtest,
        "can_forward_test": can_forward_test,
        "reason": reason.strip()
    }

def get_all_strategies() -> list[dict]:
    """Return all strategies as a list."""
    return list(STRATEGY_REGISTRY.values())


def get_strategy(strategy_id: str) -> dict | None:
    """Return a single strategy dictionary, or None if invalid."""
    return STRATEGY_REGISTRY.get(strategy_id)


def get_enabled_strategies() -> list[dict]:
    """Return strategies that are 'implemented' or 'partial'."""
    return [s for s in STRATEGY_REGISTRY.values() if s["status"] in ["implemented", "partial"]]


def get_implemented_strategies() -> list[dict]:
    """Return only fully 'implemented' strategies."""
    return [s for s in STRATEGY_REGISTRY.values() if s["status"] == "implemented"]


def get_strategies_by_category(category: str) -> list[dict]:
    """Return strategies filtered by category."""
    return [s for s in STRATEGY_REGISTRY.values() if s["category"] == category]


def get_strategy_options_for_dashboard() -> list[dict]:
    """Return a lightweight list for dashboard dropdowns."""
    options = []
    for s in STRATEGY_REGISTRY.values():
        options.append({
            "id": s["id"],
            "name": s["name"],
            "status": s["status"],
            "recommended_priority": s.get("recommended_priority", "medium"),
            "readiness": s.get("readiness", {})
        })
    return options


def validate_strategy_id(strategy_id: str) -> bool:
    """Check if strategy_id exists."""
    return strategy_id in STRATEGY_REGISTRY

def get_testable_strategies(test_type: str) -> list[dict]:
    """Return strategies that can be tested for a specific type (analysis, backtest, forward_test)."""
    if test_type == "backtest":
        return get_backtestable_strategies()
    elif test_type == "forward_test" or test_type == "forwardtest":
        return get_forward_testable_strategies()
    else:
        return [s for s in STRATEGY_REGISTRY.values() if s.get("testability", {}).get("can_analyze", False)]

def get_backtestable_strategies() -> list[dict]:
    """Return strategies that can be backtested."""
    return [s for s in STRATEGY_REGISTRY.values() if s.get("testability", {}).get("can_backtest", False)]

def get_forward_testable_strategies() -> list[dict]:
    """Return strategies that can be forward tested."""
    return [s for s in STRATEGY_REGISTRY.values() if s.get("testability", {}).get("can_forward_test", False)]
