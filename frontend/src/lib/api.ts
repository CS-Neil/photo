const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ProviderModel {
  id: string;
  name: string;
}

export interface ProviderInfo {
  id: string;
  name: string;
  base_url: string;
  api_format: string;
  models: ProviderModel[];
}

export interface LLMConfig {
  provider: string;
  apiKey: string;
  model: string;
  baseUrl: string;
  apiFormat: string;
}

export interface AnalyzeResult {
  histograms: {
    red: number[];
    green: number[];
    blue: number[];
    luminance: number[];
  };
  tone: Record<string, any>;
  color: Record<string, any>;
  description: string;
}

export interface MatchResult {
  user_tone: Record<string, any>;
  user_color: Record<string, any>;
  user_histograms: {
    red: number[];
    green: number[];
    blue: number[];
    luminance: number[];
  };
  lr_params: Record<string, any>;
  match_description: string;
}

export async function fetchProviders(): Promise<ProviderInfo[]> {
  const res = await fetch(`${API_BASE}/api/providers`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.providers;
}

export async function analyzeReference(
  file: File,
  config: LLMConfig
): Promise<AnalyzeResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("api_key", config.apiKey);
  formData.append("model", config.model);
  formData.append("provider", config.provider);
  if (config.baseUrl) {
    formData.append("base_url", config.baseUrl);
  }
  if (config.apiFormat) {
    formData.append("api_format", config.apiFormat);
  }

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Analysis failed");
  }

  return res.json();
}

export async function matchPhotos(
  file: File,
  config: LLMConfig,
  refTone: Record<string, any>,
  refColor: Record<string, any>,
  refDescription: string
): Promise<MatchResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("api_key", config.apiKey);
  formData.append("model", config.model);
  formData.append("provider", config.provider);
  if (config.baseUrl) {
    formData.append("base_url", config.baseUrl);
  }
  if (config.apiFormat) {
    formData.append("api_format", config.apiFormat);
  }
  formData.append("ref_tone", JSON.stringify(refTone));
  formData.append("ref_color", JSON.stringify(refColor));
  formData.append("ref_description", refDescription);

  const res = await fetch(`${API_BASE}/api/match`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Match failed");
  }

  return res.json();
}

export async function exportXmp(lrParams: Record<string, any>): Promise<Blob> {
  const formData = new FormData();
  formData.append("lr_params", JSON.stringify(lrParams));

  const res = await fetch(`${API_BASE}/api/export/xmp`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Export failed");
  }

  return res.blob();
}
