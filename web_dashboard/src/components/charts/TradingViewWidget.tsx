"use client";

import React, { useEffect, useRef, memo } from 'react';

type TradingViewWidgetProps = {
  symbol: string;
};

// Map internal symbols to TradingView symbols
const TV_SYMBOL_MAP: Record<string, string> = {
  "XAUUSD": "OANDA:XAUUSD",
  "NQ100": "CME_MINI:NQ1!",
  "DJI30": "DJ:DJI",
  "GBPJPY": "FX:GBPJPY",
  "USDJPY": "FX:USDJPY",
  "EURUSD": "FX:EURUSD",
  "BTCUSD": "BITSTAMP:BTCUSD",
  "ETHUSD": "BITSTAMP:ETHUSD",
  "USOIL": "TVC:USOIL"
};

function TradingViewWidget({ symbol }: TradingViewWidgetProps) {
  const container = useRef<HTMLDivElement>(null);
  
  const tvSymbol = TV_SYMBOL_MAP[symbol] || `FX:${symbol}`;

  useEffect(() => {
    // Only append if it's not already there
    if (!container.current) return;
    container.current.innerHTML = ''; // Clear out any previous widget

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = `
      {
        "autosize": true,
        "symbol": "${tvSymbol}",
        "interval": "60",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "backgroundColor": "rgba(2, 6, 23, 1)",
        "gridColor": "rgba(30, 41, 59, 1)",
        "hide_top_toolbar": true,
        "hide_legend": true,
        "save_image": false,
        "calendar": false,
        "hide_volume": true,
        "support_host": "https://www.tradingview.com"
      }`;

    container.current.appendChild(script);
  }, [tvSymbol]);

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: "420px", width: "100%" }}>
      <div className="tradingview-widget-container__widget" style={{ height: "calc(100% - 32px)", width: "100%" }}></div>
    </div>
  );
}

export default memo(TradingViewWidget);
