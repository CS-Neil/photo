"use client";

import { useState, useCallback, useEffect } from "react";
import { Camera, Loader2, KeyRound, Settings, Globe } from "lucide-react";
import ImageUploader from "../components/ImageUploader";
import HistogramChart from "../components/HistogramChart";
import AnalysisResult from "../components/AnalysisResult";
import LRParams from "../components/LRParams";
import {
  analyzeReference,
  matchPhotos,
  fetchProviders,
  AnalyzeResult,
  MatchResult,
  ProviderInfo,
  LLMConfig,
} from "../lib/api";

type Step = "setup" | "reference" | "analyze" | "user" | "result";

export default function Home() {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [selectedProvider, setSelectedProvider] = useState("anthropic");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("claude-sonnet-4-20250514");
  const [customBaseUrl, setCustomBaseUrl] = useState("");
  const [customModel, setCustomModel] = useState("");
  const [customFormat, setCustomFormat] = useState("openai");

  const [step, setStep] = useState<Step>("setup");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [refFile, setRefFile] = useState<File | null>(null);
  const [refPreview, setRefPreview] = useState<string | null>(null);
  const [refResult, setRefResult] = useState<AnalyzeResult | null>(null);

  const [userFile, setUserFile] = useState<File | null>(null);
  const [userPreview, setUserPreview] = useState<string | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);

  useEffect(() => {
    fetchProviders().then((p) => {
      if (p.length > 0) setProviders(p);
    });
  }, []);

  const currentProvider = providers.find((p) => p.id === selectedProvider);
  const currentModels = currentProvider?.models || [];
  const isCustom = selectedProvider === "custom";

  const getLLMConfig = (): LLMConfig => ({
    provider: selectedProvider,
    apiKey,
    model: isCustom ? customModel : model,
    baseUrl: isCustom ? customBaseUrl : "",
    apiFormat: isCustom ? customFormat : "",
  });

  const getDisplayModel = () => {
    if (isCustom) return customModel || "custom";
    const m = currentModels.find((m) => m.id === model);
    return m?.name || model;
  };

  const handleProviderChange = (id: string) => {
    setSelectedProvider(id);
    const prov = providers.find((p) => p.id === id);
    if (prov && prov.models.length > 0) {
      setModel(prov.models[0].id);
    }
  };

  const handleSubmit = () => {
    if (!apiKey.trim()) {
      setError("请输入 API Key");
      return;
    }
    if (isCustom && !customBaseUrl.trim()) {
      setError("自定义模式需要填写 Base URL");
      return;
    }
    if (isCustom && !customModel.trim()) {
      setError("自定义模式需要填写模型名称");
      return;
    }
    setError("");
    setStep("reference");
  };

  const handleRefSelect = useCallback((file: File) => {
    setRefFile(file);
    setRefPreview(URL.createObjectURL(file));
    setRefResult(null);
    setMatchResult(null);
  }, []);

  const handleAnalyze = async () => {
    if (!refFile) return;
    setLoading(true);
    setError("");
    try {
      const result = await analyzeReference(refFile, getLLMConfig());
      setRefResult(result);
      setStep("analyze");
    } catch (e: any) {
      setError(e.message || "分析失败");
    } finally {
      setLoading(false);
    }
  };

  const handleUserSelect = useCallback((file: File) => {
    setUserFile(file);
    setUserPreview(URL.createObjectURL(file));
    setMatchResult(null);
  }, []);

  const handleMatch = async () => {
    if (!userFile || !refResult) return;
    setLoading(true);
    setError("");
    try {
      const result = await matchPhotos(
        userFile,
        getLLMConfig(),
        refResult.tone,
        refResult.color,
        refResult.description
      );
      setMatchResult(result);
      setStep("result");
    } catch (e: any) {
      setError(e.message || "匹配失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <Camera className="w-8 h-8 text-[var(--primary)]" />
        <div>
          <h1 className="text-2xl font-bold">摄影调色分析</h1>
          <p className="text-sm text-[var(--muted)]">
            分析大师作品风格，生成 Lightroom 调色参数
          </p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Step 1: Setup */}
      {step === "setup" && (
        <div className="max-w-lg mx-auto space-y-4">
          <div className="bg-[var(--card)] rounded-xl p-6 border border-[var(--card-border)]">
            <div className="flex items-center gap-2 mb-4">
              <KeyRound className="w-5 h-5 text-[var(--primary)]" />
              <h2 className="font-medium">模型设置</h2>
            </div>

            {/* Provider Selection */}
            <label className="block text-sm text-[var(--muted)] mb-1.5">
              服务商
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-4">
              {providers.map((p) => (
                <button
                  key={p.id}
                  onClick={() => handleProviderChange(p.id)}
                  className={`px-3 py-2 rounded-lg text-sm border transition-colors ${
                    selectedProvider === p.id
                      ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                      : "border-[var(--card-border)] hover:border-[var(--muted)]"
                  }`}
                >
                  {p.name}
                </button>
              ))}
              {providers.length === 0 && (
                <>
                  <button
                    onClick={() => setSelectedProvider("anthropic")}
                    className="px-3 py-2 rounded-lg text-sm border border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                  >
                    Anthropic
                  </button>
                  <button
                    onClick={() => setSelectedProvider("openai")}
                    className="px-3 py-2 rounded-lg text-sm border border-[var(--card-border)] hover:border-[var(--muted)]"
                  >
                    OpenAI
                  </button>
                </>
              )}
            </div>

            {/* Custom Base URL (for custom provider) */}
            {isCustom && (
              <>
                <label className="block text-sm text-[var(--muted)] mb-1.5">
                  Base URL
                </label>
                <div className="flex items-center gap-2 mb-4">
                  <Globe className="w-4 h-4 text-[var(--muted)] flex-shrink-0" />
                  <input
                    type="text"
                    value={customBaseUrl}
                    onChange={(e) => setCustomBaseUrl(e.target.value)}
                    placeholder="https://your-api.com/v1"
                    className="flex-1 px-4 py-2.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm focus:outline-none focus:border-[var(--primary)]"
                  />
                </div>

                <label className="block text-sm text-[var(--muted)] mb-1.5">
                  API 格式
                </label>
                <div className="flex gap-2 mb-4">
                  <button
                    onClick={() => setCustomFormat("openai")}
                    className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                      customFormat === "openai"
                        ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                        : "border-[var(--card-border)] hover:border-[var(--muted)]"
                    }`}
                  >
                    OpenAI 兼容
                  </button>
                  <button
                    onClick={() => setCustomFormat("anthropic")}
                    className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                      customFormat === "anthropic"
                        ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                        : "border-[var(--card-border)] hover:border-[var(--muted)]"
                    }`}
                  >
                    Anthropic
                  </button>
                </div>
                <p className="text-xs text-[var(--muted)] mb-4">
                  大多数第三方代理/中转使用 OpenAI 兼容格式 (/v1/chat/completions)
                </p>

                <label className="block text-sm text-[var(--muted)] mb-1.5">
                  模型名称
                </label>
                <input
                  type="text"
                  value={customModel}
                  onChange={(e) => setCustomModel(e.target.value)}
                  placeholder="model-name"
                  className="w-full px-4 py-2.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm focus:outline-none focus:border-[var(--primary)] mb-4"
                />
              </>
            )}

            {/* Model Selection (for preset providers) */}
            {!isCustom && currentModels.length > 0 && (
              <>
                <label className="block text-sm text-[var(--muted)] mb-1.5">
                  模型
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm focus:outline-none focus:border-[var(--primary)] appearance-none mb-4"
                >
                  {currentModels.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </>
            )}

            {/* API Key */}
            <label className="block text-sm text-[var(--muted)] mb-1.5">
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={
                selectedProvider === "anthropic"
                  ? "sk-ant-..."
                  : selectedProvider === "openai"
                  ? "sk-..."
                  : "your-api-key"
              }
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm focus:outline-none focus:border-[var(--primary)]"
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            />
            <p className="text-xs text-[var(--muted)] mt-1.5">
              Key 仅在浏览器中使用，直接发送到对应 API，不存储到服务器
            </p>

            <button
              onClick={handleSubmit}
              className="mt-5 w-full py-2.5 rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white text-sm font-medium transition-colors"
            >
              继续
            </button>
          </div>
        </div>
      )}

      {/* Step 2+: Main Flow */}
      {step !== "setup" && (
        <div className="space-y-6">
          {/* Settings bar */}
          <div className="flex items-center justify-between bg-[var(--card)] rounded-lg px-4 py-2 border border-[var(--card-border)]">
            <div className="flex items-center gap-4 text-sm">
              <span className="text-[var(--muted)]">
                {currentProvider?.name || selectedProvider}
              </span>
              <span className="text-[var(--foreground)]">{getDisplayModel()}</span>
            </div>
            <button
              onClick={() => setStep("setup")}
              className="flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
            >
              <Settings className="w-3.5 h-3.5" />
              修改设置
            </button>
          </div>

          <section>
            <h2 className="text-lg font-medium mb-3">1. 参考图片</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <ImageUploader
                  label="上传大师参考图"
                  onFileSelect={handleRefSelect}
                  preview={refPreview}
                />
                {refFile && !refResult && (
                  <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="mt-3 w-full py-2.5 rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                    分析参考图
                  </button>
                )}
                {refResult && (
                  <button
                    onClick={() => {
                      setRefFile(null);
                      setRefPreview(null);
                      setRefResult(null);
                      setMatchResult(null);
                      setStep("reference");
                    }}
                    className="mt-3 w-full py-2 rounded-lg border border-[var(--card-border)] text-sm text-[var(--muted)] hover:text-white transition-colors"
                  >
                    更换参考图
                  </button>
                )}
              </div>
              {refResult && (
                <div>
                  <HistogramChart
                    histograms={refResult.histograms}
                    title="参考图直方图"
                  />
                </div>
              )}
            </div>
            {refResult && (
              <div className="mt-4">
                <AnalysisResult
                  tone={refResult.tone}
                  color={refResult.color}
                  description={refResult.description}
                />
              </div>
            )}
          </section>

          {/* Step 3: Upload User Photo */}
          {refResult && (
            <section>
              <h2 className="text-lg font-medium mb-3">2. 你的照片</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <ImageUploader
                    label="上传你的照片"
                    onFileSelect={handleUserSelect}
                    preview={userPreview}
                  />
                  {userFile && !matchResult && (
                    <button
                      onClick={handleMatch}
                      disabled={loading}
                      className="mt-3 w-full py-2.5 rounded-lg bg-[var(--accent)] hover:opacity-90 text-white text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                      生成调色参数
                    </button>
                  )}
                </div>
                {matchResult && (
                  <div>
                    <HistogramChart
                      histograms={matchResult.user_histograms}
                      title="你的照片直方图"
                    />
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Step 4: Results */}
          {matchResult && (
            <section>
              <h2 className="text-lg font-medium mb-3">3. 调色参数</h2>
              <LRParams
                lrParams={matchResult.lr_params}
                matchDescription={matchResult.match_description}
              />
            </section>
          )}
        </div>
      )}
    </main>
  );
}
