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

    # --- New dimensions ---

    # 1. Light quality: analyze transition sharpness via Sobel gradient
    gray_u8 = gray.astype(np.uint8)
    sobel_x = cv2.Sobel(gray_u8, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray_u8, cv2.CV_64F, 0, 1, ksize=3)
    gradient_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    transition_sharpness = float(np.mean(gradient_mag))

    if transition_sharpness > 40:
        light_quality = "hard"
    elif transition_sharpness < 20:
        light_quality = "soft"
    else:
        light_quality = "mixed"

    # 2. Local contrast: difference between original and blurred version
    blurred = cv2.GaussianBlur(gray_u8, (31, 31), 0).astype(np.float64)
    local_diff = np.abs(gray - blurred)
    local_contrast = float(np.mean(local_diff))

    # 3. Histogram smoothness: how smooth the tonal transitions are
    hist = cv2.calcHist([gray_u8], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_diff = np.abs(np.diff(hist_norm))
    histogram_smoothness = float(1.0 - np.clip(np.mean(hist_diff) * 256, 0, 1))

    # 4. Spatial brightness distribution: 3x3 grid
    h, w = gray.shape
    zone_h, zone_w = h // 3, w // 3
    zone_brightness = []
    for row in range(3):
        row_vals = []
        for col in range(3):
            zone = gray[row * zone_h:(row + 1) * zone_h, col * zone_w:(col + 1) * zone_w]
            row_vals.append(round(float(np.mean(zone)), 1))
        zone_brightness.append(row_vals)

    center_brightness = zone_brightness[1][1]
    edge_values = [
        zone_brightness[0][0], zone_brightness[0][1], zone_brightness[0][2],
        zone_brightness[1][0], zone_brightness[1][2],
        zone_brightness[2][0], zone_brightness[2][1], zone_brightness[2][2],
    ]
    edge_mean = sum(edge_values) / len(edge_values)
    brightness_center_weight = round(center_brightness / (edge_mean + 1e-10), 2)

    # 5. Lighting ratio: highlight mean / shadow mean
    shadow_mask = gray < 85
    highlight_mask = gray > 170
    shadow_mean = float(np.mean(gray[shadow_mask])) if np.any(shadow_mask) else 42.5
    highlight_mean = float(np.mean(gray[highlight_mask])) if np.any(highlight_mask) else 212.5
    lighting_ratio = round(highlight_mean / (shadow_mean + 1e-10), 2)

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
        # New dimensions
        "light_quality": light_quality,
        "transition_sharpness": round(transition_sharpness, 1),
        "local_contrast": round(local_contrast, 1),
        "histogram_smoothness": round(histogram_smoothness, 3),
        "zone_brightness": zone_brightness,
        "brightness_center_weight": brightness_center_weight,
        "lighting_ratio": lighting_ratio,
    }
