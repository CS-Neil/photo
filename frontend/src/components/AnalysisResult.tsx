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
  const lightMap: Record<string, string> = { hard: "硬光", soft: "柔光", mixed: "混合光" };
  const harmonyMap: Record<string, string> = {
    complementary: "互补色",
    analogous: "类似色",
    triadic: "三角色",
    split_complementary: "分裂互补",
    monochromatic: "单色系",
    mixed: "混合",
  };
  const moodMap: Record<string, string> = {
    warm_vibrant: "暖调鲜艳",
    warm_muted: "暖调柔和",
    cool_vibrant: "冷调鲜艳",
    cool_muted: "冷调柔和",
    dramatic: "戏剧性",
    neutral: "中性",
  };
  const uniformityMap: Record<string, string> = { high: "高", medium: "中等", low: "低" };
  const separationMap: Record<string, string> = { high: "高", medium: "中等", low: "低" };

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
          <div>
            <span className="text-[var(--muted)]">光线质感: </span>
            <span>{lightMap[tone.light_quality] || tone.light_quality}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">局部对比度: </span>
            <span>{tone.local_contrast}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">光比: </span>
            <span>{tone.lighting_ratio}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">影调连续性: </span>
            <span>{tone.histogram_smoothness}</span>
          </div>
        </div>

        {/* Shadow/Midtone/Highlight bar */}
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

        {/* Zone brightness heatmap */}
        {tone.zone_brightness && (
          <div className="mt-3">
            <span className="text-xs text-[var(--muted)]">明暗空间分布:</span>
            <div className="grid grid-cols-3 gap-1 mt-1 w-32">
              {tone.zone_brightness.flat().map((val: number, i: number) => {
                const opacity = val / 255;
                return (
                  <div
                    key={i}
                    className="aspect-square rounded-sm flex items-center justify-center text-[9px] font-mono"
                    style={{
                      backgroundColor: `rgba(255, 255, 255, ${opacity})`,
                      color: opacity > 0.5 ? "#000" : "#fff",
                      border: "1px solid var(--card-border)",
                    }}
                  >
                    {Math.round(val)}
                  </div>
                );
              })}
            </div>
            <span className="text-[10px] text-[var(--muted)] mt-1 block">
              中心权重: {tone.brightness_center_weight}
            </span>
          </div>
        )}
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
          <div>
            <span className="text-[var(--muted)]">色彩情绪: </span>
            <span>{moodMap[color.color_mood] || color.color_mood}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">色彩和谐: </span>
            <span>{harmonyMap[color.color_harmony?.type] || color.color_harmony?.type}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">色彩分离度: </span>
            <span>{separationMap[color.color_separation] || color.color_separation}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">饱和度一致性: </span>
            <span>{uniformityMap[color.saturation_uniformity] || color.saturation_uniformity}</span>
          </div>
          <div>
            <span className="text-[var(--muted)]">色偏: </span>
            <span>
              {color.color_cast?.direction
                ? `偏${color.color_cast.direction} (${color.color_cast.strength})`
                : "无"}
            </span>
          </div>
        </div>

        {/* Warm/Cool ratio bar */}
        {(color.warm_ratio !== undefined && color.cool_ratio !== undefined) && (
          <div className="mt-3">
            <span className="text-xs text-[var(--muted)]">冷暖比例:</span>
            <div className="flex gap-0 h-3 rounded overflow-hidden mt-1 text-[10px]">
              <div
                className="bg-orange-400 flex items-center justify-center text-black"
                style={{ width: `${color.warm_ratio * 100}%`, minWidth: color.warm_ratio > 0.05 ? "20px" : "0" }}
              >
                {color.warm_ratio > 0.05 ? `${(color.warm_ratio * 100).toFixed(0)}%` : ""}
              </div>
              <div
                className="bg-gray-400 flex-1 flex items-center justify-center"
              />
              <div
                className="bg-blue-400 flex items-center justify-center text-black"
                style={{ width: `${color.cool_ratio * 100}%`, minWidth: color.cool_ratio > 0.05 ? "20px" : "0" }}
              >
                {color.cool_ratio > 0.05 ? `${(color.cool_ratio * 100).toFixed(0)}%` : ""}
              </div>
            </div>
            <div className="mt-0.5 flex justify-between text-[10px] text-[var(--muted)]">
              <span>暖色</span>
              <span>冷色</span>
            </div>
          </div>
        )}

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
