"""
Detector Module
================
OpenCV contour-based object detection.

Contains ONLY:
    * ObjectDetector

The detection pipeline (grayscale -> Gaussian blur -> adaptive threshold ->
morphological closing -> contour detection -> area filtering -> object
counting) is preserved exactly as in the original implementation.
"""

from datetime import datetime

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ══════════════════════════════════════════════════════════════════════════════
#  OBJECT DETECTOR  (OpenCV contour-based)
# ══════════════════════════════════════════════════════════════════════════════
class ObjectDetector:
    """Detects and counts objects in a camera frame using OpenCV contours."""

    def __init__(self):
        self.min_area = 800
        self.max_area = 80000
        self.zone = None  # (x1,y1,x2,y2) in 0.0-1.0 relative coords

    def set_zone(self, x1, y1, x2, y2):
        self.zone = (min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2))

    def clear_zone(self):
        self.zone = None

    def detect(self, pil_image):
        if not HAS_CV2:
            return pil_image, 0

        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        h, w  = frame.shape[:2]

        if self.zone:
            zx1 = int(self.zone[0] * w)
            zy1 = int(self.zone[1] * h)
            zx2 = int(self.zone[2] * w)
            zy2 = int(self.zone[3] * h)
            dim = (frame * 0.3).astype(np.uint8)
            frame_display = dim.copy()
            frame_display[zy1:zy2, zx1:zx2] = frame[zy1:zy2, zx1:zx2]
            cv2.rectangle(frame_display, (zx1, zy1), (zx2, zy2), (0, 229, 255), 2)
            cv2.putText(frame_display, "SHELF ZONE", (zx1+4, zy1+16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 229, 255), 1)
            roi = frame[zy1:zy2, zx1:zx2]
        else:
            frame_display = frame.copy()
            roi = frame
            zx1, zy1 = 0, 0

        gray   = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur   = cv2.GaussianBlur(gray, (11, 11), 0)
        thresh = cv2.adaptiveThreshold(blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 35, 8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_area < area < self.max_area:
                count += 1
                x, y, bw, bh = cv2.boundingRect(cnt)
                fx, fy = x + zx1, y + zy1
                cv2.rectangle(frame_display, (fx, fy), (fx+bw, fy+bh), (0, 255, 100), 2)
                cv2.putText(frame_display, f"#{count}", (fx+4, fy+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 100), 2)

        cv2.rectangle(frame_display, (0, 0), (230, 32), (0, 0, 0), -1)
        cv2.putText(frame_display, f"DETECTED: {count}", (6, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 229, 255), 2)
        ts = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame_display, ts, (w-75, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 229, 255), 1)
        if not self.zone:
            cv2.putText(frame_display, "Drag on feed to set shelf zone",
                        (6, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120,120,120), 1)

        return Image.fromarray(cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)), count
