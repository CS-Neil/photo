import httpx


PRESET_PROVIDERS = [
    {
        "id": "anthropic",
        "name": "Anthropic (Claude)",
        "base_url": "https://api.anthropic.com",
        "api_format": "anthropic",
        "models": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
            {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5"},
            {"id": "claude-opus-4-20250514", "name": "Claude Opus 4"},
        ],
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "api_format": "openai",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ],
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "api_format": "openai",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat"},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner"},
        ],
    },
    {
        "id": "zhipu",
        "name": "智谱 (Zhipu)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_format": "openai",
        "models": [
            {"id": "glm-4-plus", "name": "GLM-4 Plus"},
            {"id": "glm-4-flash", "name": "GLM-4 Flash"},
        ],
    },
    {
        "id": "custom",
        "name": "自定义 (OpenAI 兼容)",
        "base_url": "",
        "api_format": "openai",
        "models": [],
    },
]


ANALYZE_PROMPT = """你是一位专业摄影师和调色师。请根据以下图像分析数据，用中文描述这张照片的影调和色彩特点。

## 影调数据
- 平均亮度: {mean_brightness}/255
- 标准差(对比度): {std_brightness}
- 偏度: {skewness}
- 调性: {key}调
- 对比度级别: {contrast_level}
- 阴影占比: {shadow_ratio:.1%}, 中间调占比: {midtone_ratio:.1%}, 高光占比: {highlight_ratio:.1%}
- 动态范围: {dynamic_range}

## 色彩数据
- 色温倾向: {temperature} (约{temperature_kelvin}K)
- 整体饱和度: {saturation_level} ({mean_saturation}/255)
- 主色调: {dominant_hue}
- 阴影色偏: R{shadow_r} G{shadow_g} B{shadow_b}
- 高光色偏: R{highlight_r} G{highlight_g} B{highlight_b}
- 主色板: {palette_desc}

请从以下方面描述:
1. **影调特点**: 整体明暗、对比度风格、光影氛围
2. **色彩特点**: 色温氛围、主色调搭配、阴影/高光的色彩倾向、饱和度风格
3. **整体风格**: 用2-3句话概括这张照片的视觉风格和情绪

请保持专业但易懂，约200-300字。"""


MATCH_PROMPT = """你是一位专业调色师。用户想要将自己的照片调成参考图的风格。

## 参考图风格
{ref_description}

## 算法计算出的 Lightroom 调整参数
{params_json}

请基于以上信息，用中文给出:
1. **调色思路**: 简要说明整体调色方向和要达到的效果 (3-4句话)
2. **参数解读**: 解释为什么需要做这些调整，帮助用户理解每组参数的目的
3. **微调建议**: 算法参数可能不完美，给出1-2个手动微调建议

请保持简洁专业，约200字。"""


async def call_openai_compatible(base_url: str, api_key: str, model: str, prompt: str) -> str:
    """Call any OpenAI-compatible API (GPT, DeepSeek, Zhipu, etc.)."""
    base = base_url.rstrip("/")
    # Auto-detect path: if base_url already ends with /v1, use it directly;
    # otherwise append /v1 for the standard OpenAI path
    if base.endswith("/v1"):
        url = f"{base}/chat/completions"
    else:
        url = f"{base}/v1/chat/completions"

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        if resp.status_code != 200:
            text = resp.text[:500]
            raise RuntimeError(f"API returned {resp.status_code}: {text}")
        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(f"API returned non-JSON response: {resp.text[:300]}")
        if "choices" not in data:
            raise RuntimeError(f"Unexpected response format: {str(data)[:300]}")
        return data["choices"][0]["message"]["content"]


async def call_anthropic(base_url: str, api_key: str, model: str, prompt: str) -> str:
    """Call Anthropic API."""
    base = base_url.rstrip("/")
    # If base_url already contains /v1, don't double it
    if base.endswith("/v1"):
        url = f"{base}/messages"
    else:
        url = f"{base}/v1/messages"

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            url,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        if resp.status_code != 200:
            text = resp.text[:500]
            raise RuntimeError(f"API returned {resp.status_code}: {text}")
        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(f"API returned non-JSON response: {resp.text[:300]}")
        if "content" not in data:
            raise RuntimeError(f"Unexpected response format: {str(data)[:300]}")
        return data["content"][0]["text"]


async def call_llm(base_url: str, api_key: str, model: str, api_format: str, prompt: str) -> str:
    """Unified LLM call dispatcher."""
    if api_format == "anthropic":
        return await call_anthropic(base_url, api_key, model, prompt)
    else:
        return await call_openai_compatible(base_url, api_key, model, prompt)


def resolve_provider(provider_id: str) -> dict:
    """Look up a preset provider by id."""
    for p in PRESET_PROVIDERS:
        if p["id"] == provider_id:
            return p
    return PRESET_PROVIDERS[-1]  # fallback to custom


async def analyze_with_llm(
    api_key: str,
    tone: dict,
    color: dict,
    model: str = "claude-sonnet-4-20250514",
    base_url: str = "https://api.anthropic.com",
    api_format: str = "anthropic",
) -> str:
    """Generate natural language description of the image."""
    palette_desc = ", ".join(
        f"{p['hex']}({p['proportion']:.0%})" for p in color["palette"][:5]
    )

    prompt = ANALYZE_PROMPT.format(
        mean_brightness=tone["mean_brightness"],
        std_brightness=tone["std_brightness"],
        skewness=tone["skewness"],
        key={"high": "高", "mid": "中间", "low": "低"}[tone["key"]],
        contrast_level={"high": "高", "medium": "中等", "low": "低"}[tone["contrast_level"]],
        shadow_ratio=tone["shadow_ratio"],
        midtone_ratio=tone["midtone_ratio"],
        highlight_ratio=tone["highlight_ratio"],
        dynamic_range=tone["dynamic_range"],
        temperature={"warm": "偏暖", "cool": "偏冷", "neutral": "中性"}[color["temperature"]],
        temperature_kelvin=color["temperature_kelvin"],
        saturation_level={"high": "高", "medium": "中等", "low": "低"}[color["saturation_level"]],
        mean_saturation=color["mean_saturation"],
        dominant_hue=color["dominant_hue"],
        shadow_r=color["shadow_color"]["r"],
        shadow_g=color["shadow_color"]["g"],
        shadow_b=color["shadow_color"]["b"],
        highlight_r=color["highlight_color"]["r"],
        highlight_g=color["highlight_color"]["g"],
        highlight_b=color["highlight_color"]["b"],
        palette_desc=palette_desc,
    )

    return await call_llm(base_url, api_key, model, api_format, prompt)


async def match_with_llm(
    api_key: str,
    ref_description: str,
    params: dict,
    model: str = "claude-sonnet-4-20250514",
    base_url: str = "https://api.anthropic.com",
    api_format: str = "anthropic",
) -> str:
    """Explain the matching parameters."""
    import json

    prompt = MATCH_PROMPT.format(
        ref_description=ref_description,
        params_json=json.dumps(params, indent=2, ensure_ascii=False),
    )

    return await call_llm(base_url, api_key, model, api_format, prompt)
