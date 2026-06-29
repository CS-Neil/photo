import numpy as np
import cv2


def analyze_tone(img_bgr: np.ndarray) -> dict:
    """Analyze tonal characteristics of the image."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    total_pixels = gray.size

    mean_brightness = float(np.mean(gray))
    std_brightness = float(np.std(gray))
    skewness = float(((gray - mean_brightness) ** 3).mean() / (std_brightness ** 3 + 1e-10))

    shadow_pixels = np.sum(gray < 85)
    midtone_pixels = np.sum((gray >= 85) & (gray <= 170))
    highlight_pixels = np.sum(gray > 170)

    shadow_ratio = float(shadow_pixels / total_pixels)
    midtone_ratio = float(midtone_pixels / total_pixels)
    highlight_ratio = float(highlight_pixels / total_pixels)

    # Key classification
    if mean_brightness > 170:
        key = "high"
    elif mean_brightness < 85:
        key = "low"
    else:
        key = "mid"

    # Contrast classification
    if std_brightness > 70:
        contrast_level = "high"
    elif std_brightness < 40:
        contrast_level = "low"
    else:
        contrast_level = "medium"

    # Dynamic range
    p1 = float(np.percentile(gray, 1))
    p99 = float(np.percentile(gray, 99))
    dynamic_range = p99 - p1

    return {
        "mean_brightness": round(mean_brightness, 1),
        "std_brightness": round(std_brightness, 1),
        "skewness": round(skewness, 2),
        "shadow_ratio": round(shadow_ratio, 3),
        "midtone_ratio": round(midtone_ratio, 3),
        "highlight_ratio": round(highlight_ratio, 3),
        "key": key,
        "contrast_level": contrast_level,
        "dynamic_range": round(dynamic_range, 1),
        "percentile_1": round(p1, 1),
        "percentile_99": round(p99, 1),
    }
