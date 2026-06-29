import numpy as np
import cv2
from sklearn.cluster import KMeans


def _classify_harmony(hues_deg: list[float]) -> tuple[str, float]:
    """Classify color harmony type based on dominant palette hues."""
    if len(hues_deg) < 2:
        return "monochromatic", 1.0

    hues = sorted(hues_deg)
    diffs = []
    for i in range(len(hues)):
        diff = (hues[(i + 1) % len(hues)] - hues[i]) % 360
        diffs.append(diff)

    max_diff = max(diffs)
    min_diff = min(diffs)
    spread = max_diff - min_diff

    # Check for monochromatic (all hues within 30°)
    hue_range = (hues[-1] - hues[0]) % 360
    if hue_range < 30 or (360 - hue_range) < 30:
        return "monochromatic", 0.9

    # Check for complementary (two clusters ~180° apart)
    if len(hues) >= 2:
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                angle = abs((hues[j] - hues[i]) % 360)
                if angle > 180:
                    angle = 360 - angle
                if 150 < angle < 210:
                    return "complementary", round(1.0 - abs(angle - 180) / 30, 2)

    # Check for triadic (three clusters ~120° apart)
    if len(hues) >= 3:
        for i in range(len(hues) - 2):
            d1 = (hues[i + 1] - hues[i]) % 360
            d2 = (hues[i + 2] - hues[i + 1]) % 360
            if 90 < d1 < 150 and 90 < d2 < 150:
                return "triadic", 0.8

    # Check for analogous (hues within 60°)
    if hue_range < 60 or (360 - hue_range) < 60:
        return "analogous", 0.85

    # Split complementary
    if len(hues) >= 3:
        for i in range(len(hues)):
            base = hues[i]
            complement = (base + 180) % 360
            near_complement = sum(
                1 for h in hues if h != base and min(abs(h - complement), 360 - abs(h - complement)) < 40
            )
            if near_complement >= 2:
                return "split_complementary", 0.75

    return "mixed", 0.5


def analyze_color(img_bgr: np.ndarray) -> dict:
    """Analyze color characteristics of the image."""
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float64)

    h, s, v = cv2.split(img_hsv)

    # Overall saturation
    mean_saturation = float(np.mean(s))
    saturation_level = "high" if mean_saturation > 150 else ("low" if mean_saturation < 70 else "medium")

    # Color temperature estimation (R/B ratio)
    b, g, r = cv2.split(img_bgr.astype(np.float64))
    rb_ratio = float(np.mean(r) / (np.mean(b) + 1e-10))
    if rb_ratio > 1.2:
        temperature = "warm"
    elif rb_ratio < 0.85:
        temperature = "cool"
    else:
        temperature = "neutral"

    # Approximate Kelvin estimation
    temp_kelvin = int(4000 + (rb_ratio - 1.0) * 3000)
    temp_kelvin = max(2500, min(10000, temp_kelvin))

    # Hue distribution (split into 12 sectors of 30 degrees)
    hue_hist = cv2.calcHist([img_hsv.astype(np.uint8)], [0], None, [12], [0, 180]).flatten()
    hue_hist_norm = (hue_hist / hue_hist.sum()).tolist()

    hue_labels = [
        "Red", "Orange", "Yellow", "Yellow-Green",
        "Green", "Cyan-Green", "Cyan", "Blue-Cyan",
        "Blue", "Purple", "Magenta", "Red-Magenta"
    ]
    dominant_hue_idx = int(np.argmax(hue_hist))
    dominant_hue = hue_labels[dominant_hue_idx]

    # Zone-based color shift (shadows, midtones, highlights)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    shadow_mask = gray < 85
    midtone_mask = (gray >= 85) & (gray <= 170)
    highlight_mask = gray > 170

    def zone_avg_color(mask):
        if np.sum(mask) == 0:
            return {"r": 128, "g": 128, "b": 128, "hue": 0}
        zone_r = float(np.mean(r[mask]))
        zone_g = float(np.mean(g[mask]))
        zone_b = float(np.mean(b[mask]))
        zone_h = float(np.mean(h[mask]))
        return {
            "r": round(zone_r, 1),
            "g": round(zone_g, 1),
            "b": round(zone_b, 1),
            "hue": round(zone_h * 2, 1),  # OpenCV hue is 0-180, convert to 0-360
        }

    shadow_color = zone_avg_color(shadow_mask)
    midtone_color = zone_avg_color(midtone_mask)
    highlight_color = zone_avg_color(highlight_mask)

    # Dominant colors via K-means
    pixels = img_rgb.reshape(-1, 3).astype(np.float64)
    sample_size = min(10000, len(pixels))
    indices = np.random.choice(len(pixels), sample_size, replace=False)
    sampled = pixels[indices]

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(sampled)
    centers = kmeans.cluster_centers_.astype(int).tolist()
    labels_count = np.bincount(kmeans.labels_)
    proportions = (labels_count / labels_count.sum()).tolist()

    palette = []
    for color_rgb, proportion in sorted(zip(centers, proportions), key=lambda x: -x[1]):
        palette.append({
            "rgb": color_rgb,
            "hex": "#{:02x}{:02x}{:02x}".format(*color_rgb),
            "proportion": round(proportion, 3),
        })

    # --- New dimensions ---

    # 1. Color harmony classification
    palette_hues = []
    for c in centers:
        c_arr = np.uint8([[c]])
        c_hsv = cv2.cvtColor(c_arr, cv2.COLOR_RGB2HSV)[0][0]
        if c_hsv[1] > 30:  # only consider saturated colors
            palette_hues.append(float(c_hsv[0]) * 2)  # convert to 0-360
    harmony_type, harmony_score = _classify_harmony(palette_hues)

    # 2. Warm/cool ratio
    # Warm: 0-60°, 300-360°; Cool: 150-270° (in OpenCV 0-180 scale)
    h_flat = h.flatten()
    s_flat = s.flatten()
    # Only count pixels with meaningful saturation
    saturated_mask = s_flat > 30
    h_saturated = h_flat[saturated_mask]
    total_saturated = len(h_saturated) if len(h_saturated) > 0 else 1

    warm_pixels = np.sum((h_saturated < 30) | (h_saturated > 150))  # 0-60° or 300-360°
    cool_pixels = np.sum((h_saturated >= 75) & (h_saturated <= 135))  # 150-270°
    warm_ratio = float(warm_pixels / total_saturated)
    cool_ratio = float(cool_pixels / total_saturated)
    warm_cool_contrast = round(abs(warm_ratio - cool_ratio), 3)

    # 3. Saturation consistency
    saturation_std = float(np.std(s))
    if saturation_std < 30:
        saturation_uniformity = "high"
    elif saturation_std > 60:
        saturation_uniformity = "low"
    else:
        saturation_uniformity = "medium"

    # 4. Color separation (average ΔE in Lab space)
    img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2Lab)
    centers_bgr = np.array([[c[::-1] for c in centers]], dtype=np.uint8)
    centers_lab = cv2.cvtColor(centers_bgr, cv2.COLOR_BGR2Lab)[0].astype(np.float64)
    delta_e_values = []
    for i in range(len(centers_lab)):
        for j in range(i + 1, len(centers_lab)):
            de = np.sqrt(np.sum((centers_lab[i] - centers_lab[j]) ** 2))
            delta_e_values.append(de)
    avg_color_distance = float(np.mean(delta_e_values)) if delta_e_values else 0.0

    if avg_color_distance > 80:
        color_separation_level = "high"
    elif avg_color_distance < 40:
        color_separation_level = "low"
    else:
        color_separation_level = "medium"

    # 5. Color cast detection (analyze neutral/low-saturation areas)
    neutral_mask = s.flatten() < 25
    if np.sum(neutral_mask) > 100:
        r_flat = r.flatten()[neutral_mask]
        g_flat = g.flatten()[neutral_mask]
        b_flat = b.flatten()[neutral_mask]
        mean_rgb = np.array([np.mean(r_flat), np.mean(g_flat), np.mean(b_flat)])
        gray_val = np.mean(mean_rgb)
        deviation = mean_rgb - gray_val
        max_dev_idx = int(np.argmax(np.abs(deviation)))
        cast_strength = float(np.abs(deviation[max_dev_idx]))
        cast_directions = ["red", "green", "blue"]
        if cast_strength > 5:
            color_cast_direction = cast_directions[max_dev_idx]
        else:
            color_cast_direction = None
            cast_strength = 0.0
    else:
        color_cast_direction = None
        cast_strength = 0.0

    # 6. Color mood
    v_std = float(np.std(v))
    if temperature == "warm" and mean_saturation > 120:
        color_mood = "warm_vibrant"
    elif temperature == "warm" and mean_saturation <= 120:
        color_mood = "warm_muted"
    elif temperature == "cool" and mean_saturation > 120:
        color_mood = "cool_vibrant"
    elif temperature == "cool" and mean_saturation <= 120:
        color_mood = "cool_muted"
    elif v_std > 70 and mean_saturation > 100:
        color_mood = "dramatic"
    else:
        color_mood = "neutral"

    return {
        "mean_saturation": round(mean_saturation, 1),
        "saturation_level": saturation_level,
        "temperature": temperature,
        "temperature_kelvin": temp_kelvin,
        "rb_ratio": round(rb_ratio, 3),
        "dominant_hue": dominant_hue,
        "hue_distribution": dict(zip(hue_labels, [round(v, 3) for v in hue_hist_norm])),
        "shadow_color": shadow_color,
        "midtone_color": midtone_color,
        "highlight_color": highlight_color,
        "palette": palette,
        # New dimensions
        "color_harmony": {"type": harmony_type, "score": harmony_score},
        "warm_ratio": round(warm_ratio, 3),
        "cool_ratio": round(cool_ratio, 3),
        "warm_cool_contrast": warm_cool_contrast,
        "saturation_std": round(saturation_std, 1),
        "saturation_uniformity": saturation_uniformity,
        "avg_color_distance": round(avg_color_distance, 1),
        "color_separation": color_separation_level,
        "color_cast": {"direction": color_cast_direction, "strength": round(cast_strength, 1)},
        "color_mood": color_mood,
    }
