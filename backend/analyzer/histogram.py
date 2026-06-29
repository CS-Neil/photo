import numpy as np
import cv2


def compute_histograms(img_bgr: np.ndarray) -> dict:
    """Compute RGB and luminance histograms (256 bins each)."""
    b, g, r = cv2.split(img_bgr)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    hist_r = cv2.calcHist([r], [0], None, [256], [0, 256]).flatten().tolist()
    hist_g = cv2.calcHist([g], [0], None, [256], [0, 256]).flatten().tolist()
    hist_b = cv2.calcHist([b], [0], None, [256], [0, 256]).flatten().tolist()
    hist_l = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten().tolist()

    total = gray.size
    hist_r_norm = [v / total for v in hist_r]
    hist_g_norm = [v / total for v in hist_g]
    hist_b_norm = [v / total for v in hist_b]
    hist_l_norm = [v / total for v in hist_l]

    return {
        "red": hist_r_norm,
        "green": hist_g_norm,
        "blue": hist_b_norm,
        "luminance": hist_l_norm,
    }
