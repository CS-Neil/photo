"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface Props {
  histograms: {
    red: number[];
    green: number[];
    blue: number[];
    luminance: number[];
  };
  title?: string;
}

export default function HistogramChart({ histograms, title }: Props) {
  // Sample every 4th point, skip first and last 2 bins (extreme spikes)
  const raw = Array.from({ length: 62 }, (_, i) => {
    const idx = (i + 1) * 4;
    return {
      x: idx,
      r: histograms.red[idx] || 0,
      g: histograms.green[idx] || 0,
      b: histograms.blue[idx] || 0,
      l: histograms.luminance[idx] || 0,
    };
  });

  // Clip top 2% of values to prevent spikes from flattening the chart
  const allVals = raw.flatMap((d) => [d.r, d.g, d.b, d.l]);
  const sorted = [...allVals].sort((a, b) => a - b);
  const clipMax = sorted[Math.floor(sorted.length * 0.98)] * 1.2;

  const data = raw.map((d) => ({
    x: d.x,
    r: Math.min(d.r, clipMax),
    g: Math.min(d.g, clipMax),
    b: Math.min(d.b, clipMax),
    l: Math.min(d.l, clipMax),
  }));

  return (
    <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--card-border)]">
      {title && (
        <h3 className="text-sm font-medium mb-3 text-[var(--muted)]">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data}>
          <XAxis dataKey="x" hide />
          <YAxis hide domain={[0, "auto"]} />
          <Legend
            wrapperStyle={{ fontSize: "12px" }}
            formatter={(value: string) => {
              const map: Record<string, string> = {
                r: "R",
                g: "G",
                b: "B",
                l: "亮度",
              };
              return map[value] || value;
            }}
          />
          <Area
            type="monotone"
            dataKey="r"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.15}
            dot={false}
            strokeWidth={1.5}
          />
          <Area
            type="monotone"
            dataKey="g"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.15}
            dot={false}
            strokeWidth={1.5}
          />
          <Area
            type="monotone"
            dataKey="b"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.15}
            dot={false}
            strokeWidth={1.5}
          />
          <Area
            type="monotone"
            dataKey="l"
            stroke="#a3a3a3"
            fill="#a3a3a3"
            fillOpacity={0.08}
            dot={false}
            strokeWidth={1}
            strokeDasharray="3 3"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
