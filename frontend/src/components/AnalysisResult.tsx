"use client";

interface Props {
  tone: Record<string, any>;
  color: Record<string, any>;
  description: string;
}

export default function AnalysisResult({ tone, color, description }: Props) {
  const keyMap: Record<string, string> = { high: "高调", mid: "中间调", low: "低调" };
  const contrastMap: Record<string, string> = { high: "高", medium: "中等", low: "低" };
  const tempMap: Record<string, string> = { warm: "偏暖", cool: "偏冷", neutral: "中性" };
  const satMap: Record<string, string> = { high: "高", medium: "中等", low: "低" };

  return (
    <div className="space-y-4">
      {/* Tone Card */}
      <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--card-border)]">
        <h3 className="text-sm font-medium mb-3 text-[var(--primary)]">影调分析</h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-[var(--muted)]">调性: </span>
            <span>{keyMap[tone.key]}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">对比度: </span>
            <span>{contrastMap[tone.contrast_level]}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">平均亮度: </span>
            <span>{tone.mean_brightness}/255</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">动态范围: </span>
            <span>{tone.dynamic_range}</span>
          </div>
        </div>
        <div className="mt-3 flex gap-1 h-4 rounded overflow-hidden text-[10px]">
          <div
            className="bg-gray-800 flex items-center justify-center"
            style={{ width: `${tone.shadow_ratio * 100}%` }}
          >
            {(tone.shadow_ratio * 100).toFixed(0)}%
          </div>
          <div
            className="bg-gray-500 flex items-center justify-center"
            style={{ width: `${tone.midtone_ratio * 100}%` }}
          >
            {(tone.midtone_ratio * 100).toFixed(0)}%
          </div>
          <div
            className="bg-gray-200 text-black flex items-center justify-center"
            style={{ width: `${tone.highlight_ratio * 100}%` }}
          >
            {(tone.highlight_ratio * 100).toFixed(0)}%
          </div>
        </div>
        <div className="mt-1 flex justify-between text-[10px] text-[var(--muted)]">
          <span>阴影</span>
          <span>中间调</span>
          <span>高光</span>
        </div>
      </div>

      {/* Color Card */}
      <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--card-border)]">
        <h3 className="text-sm font-medium mb-3 text-[var(--primary)]">色彩分析</h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-[var(--muted)]">色温: </span>
            <span>{tempMap[color.temperature]} ({color.temperature_kelvin}K)</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">饱和度: </span>
            <span>{satMap[color.saturation_level]}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">主色调: </span>
            <span>{color.dominant_hue}</span>
          </div>
        </div>
        {/* Color Palette */}
        <div className="mt-3">
          <span className="text-xs text-[var(--muted)]">主色板:</span>
          <div className="flex gap-2 mt-1">
            {color.palette?.map((p: any, i: number) => (
              <div key={i} className="flex flex-col items-center">
                <div
                  className="w-8 h-8 rounded-md border border-[var(--card-border)]"
                  style={{ backgroundColor: p.hex }}
                />
                <span className="text-[10px] text-[var(--muted)] mt-1">
                  {(p.proportion * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* LLM Description */}
      {description && (
        <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--card-border)]">
          <h3 className="text-sm font-medium mb-3 text-[var(--primary)]">
            风格描述
          </h3>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {description}
          </p>
        </div>
      )}
    </div>
  );
}
