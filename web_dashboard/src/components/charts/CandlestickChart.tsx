"use client";

import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi, SeriesMarker, Time } from 'lightweight-charts';

export type Candle = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
};

export type ChartMarker = {
  time: number;
  position: "aboveBar" | "belowBar";
  color?: string;
  shape?: "arrowUp" | "arrowDown" | "circle";
  text?: string;
};

export type PriceLine = {
  price: number;
  title: string;
  color?: string;
};

export type CandlestickChartProps = {
  candles: Candle[];
  markers?: ChartMarker[];
  priceLines?: PriceLine[];
  height?: number;
  loading?: boolean;
  error?: string | null;
};

export default function CandlestickChart({
  candles,
  markers = [],
  priceLines = [],
  height = 420,
  loading = false,
  error = null,
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    // Dark theme configuration
    chartRef.current = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#A3A3A3',
      },
      grid: {
        vertLines: { color: '#1E293B' }, // slate-800
        horzLines: { color: '#1E293B' },
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: '#1E293B',
      },
      rightPriceScale: {
        borderColor: '#1E293B',
      },
      crosshair: {
        mode: 0, // Normal mode
      },
    });

    seriesRef.current = chartRef.current.addCandlestickSeries({
      upColor: '#22C55E', // green-500
      downColor: '#EF4444', // red-500
      borderVisible: false,
      wickUpColor: '#22C55E',
      wickDownColor: '#EF4444',
    });

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [height]);

  // Update data effect
  useEffect(() => {
    if (!seriesRef.current || !chartRef.current) return;

    if (candles.length > 0) {
      // lightweight-charts requires strictly ascending time order
      // Assume candles are ordered properly, but if not we should sort them
      const sortedCandles = [...candles].sort((a, b) => a.time - b.time).map(c => ({
        ...c,
        time: c.time as Time
      }));
      seriesRef.current.setData(sortedCandles);

      // Add markers
      if (markers.length > 0) {
        // Markers must also be sorted by time
        const sortedMarkers = [...markers].sort((a, b) => a.time - b.time).map(m => ({
          time: m.time as Time,
          position: m.position,
          color: m.color || (m.position === 'belowBar' ? '#22C55E' : '#EF4444'),
          shape: m.shape || (m.position === 'belowBar' ? 'arrowUp' : 'arrowDown'),
          text: m.text || '',
        }));
        seriesRef.current.setMarkers(sortedMarkers as SeriesMarker<Time>[]);
      } else {
        seriesRef.current.setMarkers([]);
      }

      // Add Price Lines
      // Clear existing first (lightweight-charts doesn't have a clearAllPriceLines)
      // So we generally re-create series or just add them. For now we just add.
      priceLines.forEach(line => {
        seriesRef.current?.createPriceLine({
          price: line.price,
          color: line.color || '#3B82F6', // blue-500
          lineWidth: 2,
          lineStyle: 2, // Dashed
          axisLabelVisible: true,
          title: line.title,
        });
      });

      chartRef.current.timeScale().fitContent();
    } else {
      seriesRef.current.setData([]);
    }
  }, [candles, markers, priceLines]);

  if (loading) {
    return (
      <div 
        className="w-full flex items-center justify-center bg-slate-950/50 border border-slate-800 rounded-md" 
        style={{ height }}
      >
        <span className="text-muted-foreground animate-pulse">Loading chart data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div 
        className="w-full flex items-center justify-center bg-slate-950/50 border border-slate-800 rounded-md" 
        style={{ height }}
      >
        <span className="text-red-500">{error}</span>
      </div>
    );
  }

  if (candles.length === 0) {
    return (
      <div 
        className="w-full flex flex-col items-center justify-center bg-slate-950/50 border border-slate-800 rounded-md" 
        style={{ height }}
      >
        <span className="text-muted-foreground">No market data available for this selection.</span>
      </div>
    );
  }

  return (
    <div className="w-full relative">
      <div ref={chartContainerRef} className="w-full border border-slate-800 rounded-md overflow-hidden bg-slate-950" />
      <div className="absolute bottom-1 right-2 z-10">
        <span className="text-[10px] text-slate-500 opacity-50">Charts powered by TradingView Lightweight Charts</span>
      </div>
    </div>
  );
}
