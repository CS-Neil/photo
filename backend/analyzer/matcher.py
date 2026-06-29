import numpy as np


def compute_lr_params(ref_tone: dict, ref_color: dict, user_tone: dict, user_color: dict) -> dict:
    """Compute Lightroom parameters to match user photo to reference."""

    # --- Basic Tone ---
    exposure_diff = (ref_tone["mean_brightness"] - user_tone["mean_brightness"]) / 255.0
    exposure = round(np.clip(exposure_diff * 5.0, -5.0, 5.0), 2)

    contrast_diff = ref_tone["std_brightness"] - user_tone["std_brightness"]
    contrast = round(np.clip(contrast_diff * 1.5, -100, 100), 0)

    # Highlights and Shadows based on zone ratios
    highlight_diff = ref_tone["highlight_ratio"] - user_tone["highlight_ratio"]
    highlights = round(np.clip(highlight_diff * 300, -100, 100), 0)

    shadow_diff = ref_tone["shadow_ratio"] - user_tone["shadow_ratio"]
    shadows = round(np.clip(-shadow_diff * 300, -100, 100), 0)

    # Whites and Blacks based on percentiles
    whites_diff = ref_tone["percentile_99"] - user_tone["percentile_99"]
    whites = round(np.clip(whites_diff * 0.8, -100, 100), 0)

    blacks_diff = ref_tone["percentile_1"] - user_tone["percentile_1"]
    blacks = round(np.clip(blacks_diff * 0.8, -100, 100), 0)

    # --- White Balance ---
    temp_diff = ref_color["temperature_kelvin"] - user_color["temperature_kelvin"]
    temperature = round(np.clip(user_color["temperature_kelvin"] + temp_diff, 2000, 50000), 0)

    ref_tint = (ref_color["midtone_color"]["g"] - 128) * 0.5
    user_tint = (user_color["midtone_color"]["g"] - 128) * 0.5
    tint = round(np.clip(ref_tint - user_tint, -150, 150), 0)

    # --- Saturation & Vibrance ---
    sat_diff = ref_color["mean_saturation"] - user_color["mean_saturation"]
    saturation = round(np.clip(sat_diff * 0.7, -100, 100), 0)
    vibrance = round(np.clip(sat_diff * 0.5, -100, 100), 0)

    # --- Tone Curve (simplified 4-point) ---
    ref_shadow_target = ref_tone["percentile_1"] / 255.0
    ref_highlight_target = ref_tone["percentile_99"] / 255.0

    tone_curve = {
        "shadows": {"x": 25, "y": round(25 + ref_shadow_target * 20)},
        "darks": {"x": 64, "y": round(64 + (ref_tone["shadow_ratio"] - 0.33) * 30)},
        "lights": {"x": 192, "y": round(192 + (ref_tone["highlight_ratio"] - 0.33) * 30)},
        "highlights": {"x": 230, "y": round(230 + (1 - ref_highlight_target) * 10)},
    }

    # --- Split Toning ---
    shadow_hue = ref_color["shadow_color"]["hue"]
    highlight_hue = ref_color["highlight_color"]["hue"]

    ref_shadow_sat = np.sqrt(
        (ref_color["shadow_color"]["r"] - 128) ** 2 +
        (ref_color["shadow_color"]["b"] - 128) ** 2
    ) * 0.5
    ref_highlight_sat = np.sqrt(
        (ref_color["highlight_color"]["r"] - 128) ** 2 +
        (ref_color["highlight_color"]["b"] - 128) ** 2
    ) * 0.5

    split_toning = {
        "shadow_hue": round(shadow_hue % 360),
        "shadow_saturation": round(np.clip(ref_shadow_sat, 0, 100)),
        "highlight_hue": round(highlight_hue % 360),
        "highlight_saturation": round(np.clip(ref_highlight_sat, 0, 100)),
        "balance": 0,
    }

    return {
        "basic": {
            "exposure": exposure,
            "contrast": int(contrast),
            "highlights": int(highlights),
            "shadows": int(shadows),
            "whites": int(whites),
            "blacks": int(blacks),
        },
        "white_balance": {
            "temperature": int(temperature),
            "tint": int(tint),
        },
        "presence": {
            "vibrance": int(vibrance),
            "saturation": int(saturation),
        },
        "tone_curve": tone_curve,
        "split_toning": split_toning,
    }
