import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from analyzer.histogram import compute_histograms
from analyzer.tone import analyze_tone
from analyzer.color import analyze_color
from analyzer.matcher import compute_lr_params
from llm.claude import analyze_with_llm, match_with_llm, PRESET_PROVIDERS, resolve_provider
from export.xmp import generate_xmp

app = FastAPI(title="Photography Color Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@app.get("/")
async def health():
    return {"status": "ok", "service": "Photography Color Analysis API"}


@app.get("/api/providers")
async def list_providers():
    """Return available providers and their models."""
    return {"providers": PRESET_PROVIDERS}


async def read_image(file: UploadFile) -> np.ndarray:
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")
    arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image format")
    h, w = img.shape[:2]
    max_dim = 2000
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    return img


@app.post("/api/analyze")
async def analyze_reference(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    model: str = Form("claude-sonnet-4-20250514"),
    base_url: str = Form(""),
    provider: str = Form("anthropic"),
    api_format: str = Form(""),
):
    """Analyze a reference image: histogram, tone, color + LLM description."""
    img = await read_image(file)

    histograms = compute_histograms(img)
    tone = analyze_tone(img)
    color = analyze_color(img)

    description = ""
    if api_key:
        prov = resolve_provider(provider)
        actual_base_url = base_url or prov["base_url"]
        actual_format = api_format or prov["api_format"]
        try:
            description = await analyze_with_llm(
                api_key, tone, color,
                model=model, base_url=actual_base_url, api_format=actual_format,
            )
        except Exception as e:
            description = f"LLM 分析失败: {str(e)}"

    return {
        "histograms": histograms,
        "tone": tone,
        "color": color,
        "description": description,
    }


@app.post("/api/match")
async def match_photos(
    file: UploadFile = File(...),
    api_key: str = Form(""),
    model: str = Form("claude-sonnet-4-20250514"),
    base_url: str = Form(""),
    provider: str = Form("anthropic"),
    api_format: str = Form(""),
    ref_tone: str = Form(...),
    ref_color: str = Form(...),
    ref_description: str = Form(""),
):
    """Compare user photo with reference and generate LR params."""
    import json

    img = await read_image(file)

    user_tone = analyze_tone(img)
    user_color = analyze_color(img)
    user_histograms = compute_histograms(img)

    ref_tone_data = json.loads(ref_tone)
    ref_color_data = json.loads(ref_color)

    lr_params = compute_lr_params(ref_tone_data, ref_color_data, user_tone, user_color)

    match_description = ""
    if api_key and ref_description:
        prov = resolve_provider(provider)
        actual_base_url = base_url or prov["base_url"]
        actual_format = api_format or prov["api_format"]
        try:
            match_description = await match_with_llm(
                api_key, ref_description, lr_params,
                model=model, base_url=actual_base_url, api_format=actual_format,
            )
        except Exception as e:
            match_description = f"LLM 分析失败: {str(e)}"

    return {
        "user_tone": user_tone,
        "user_color": user_color,
        "user_histograms": user_histograms,
        "lr_params": lr_params,
        "match_description": match_description,
    }


@app.post("/api/export/xmp")
async def export_xmp(
    lr_params: str = Form(...),
):
    """Generate and download XMP preset file."""
    import json

    params = json.loads(lr_params)
    xmp_content = generate_xmp(params)

    return Response(
        content=xmp_content,
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=color_preset.xmp"},
    )
