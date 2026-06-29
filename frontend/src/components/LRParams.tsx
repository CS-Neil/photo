"use client";

import { Download, Copy, Check } from "lucide-react";
import { useState } from "react";
import { exportXmp } from "../lib/api";

interface Props {
  lrParams: Record<string, any>;
  matchDescription: string;
}

export default function LRParams({ lrParams, matchDescription }: Props) {
  const [copied, setCopied] = useState(false);

  const basic = lrParams.basic || {};
  const wb = lrParams.white_balance || {};
  const presence = lrParams.presence || {};
  const st = lrParams.split_toning || {};

  const paramGroups = [
    {
      title: "基本调整",
      params: [
        { label: "曝光", value: basic.exposure, unit: "EV" },
        { label: "对比度", value: basic.contrast },
        { label: "高光", value: basic.highlights },
        { label: "阴影", value: basic.shadows },
        { label: "白色", value: basic.whites },
        { label: "黑色", value: basic.blacks },
      ],
    },
    {
      title: "白平衡",
      params: [
        { label: "色温", value: wb.temperature, unit: "K" },
        { label: "色调", value: wb.tint },
      ],
    },
    {
      title: "偏好",
      params: [
        { label: "清晰度", value: presence.clarity },
        { label: "自然饱和度", value: presence.vibrance },
        { label: "饱和度", value: presence.saturation },
      ],
    },
    {
      title: "色调分离",
      params: [
        { label: "阴影色相", value: st.shadow_hue, unit: "°" },
        { label: "阴影饱和度", value: st.shadow_saturation },
        { label: "高光色相", value: st.highlight_hue, unit: "°" },
        { label: "高光饱和度", value: st.highlight_saturation },
      ],
    },
  ];

  const handleExportXmp = async () => {
    try {
      const blob = await exportXmp(lrParams);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "color_preset.xmp";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("导出失败");
    }
  };

  const handleCopyText = () => {
    const text = paramGroups
      .map(
        (g) =>
          `【${g.title}】\n` +
          g.params.map((p) => `  ${p.label}: ${p.value}${p.unit || ""}`).join("\n")
      )
      .join("\n\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      {/* Match Description */}
      {matchDescription && (
        <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--card-border)]">
          <h3 className="text-sm font-medium mb-3 text-[var(--primary)]">
            调色思路
          </h3>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {matchDescription}
          </p>
        </div>
      )}

      {/* LR Params */}
      <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--card-border)]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-[var(--primary)]">
            Lightroom 参数
          </h3>
          <div className="flex gap-2">
            <button
              onClick={handleCopyText}
              className="flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-[var(--card-border)] hover:bg-[var(--muted)]/30 transition-colors"
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? "已复制" : "复制文字"}
            </button>
            <button
              onClick={handleExportXmp}
              className="flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white transition-colors"
            >
              <Download className="w-3 h-3" />
              下载 XMP
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {paramGroups.map((group) => (
            <div key={group.title}>
              <h4 className="text-xs font-medium text-[var(--muted)] mb-2">
                {group.title}
              </h4>
              <div className="space-y-1.5">
                {group.params.map((p) => (
                  <div
                    key={p.label}
                    className="flex justify-between text-sm"
                  >
                    <span className="text-[var(--muted)]">{p.label}</span>
                    <span className="font-mono">
                      {p.value}
                      {p.unit || ""}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
