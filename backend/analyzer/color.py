import numpy as np
import cv2
from sklearn.cluster import KMeans


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
    for color, proportion in sorted(zip(centers, proportions), key=lambda x: -x[1]):
        palette.append({
            "rgb": color,
            "hex": "#{:02x}{:02x}{:02x}".format(*color),
            "proportion": round(proportion, 3),
        })

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
    }
