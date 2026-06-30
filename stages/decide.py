import cv2
import numpy as np


def enhance_readability(warped: np.ndarray) -> np.ndarray:
    """
    Turn the perspective-corrected document into a clean, scanner-like
    black-and-white page: denoise -> CLAHE -> adaptive threshold -> despeckle.
    """

    if warped.ndim == 3:
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    else:
        gray = warped

    gray = cv2.medianBlur(gray, 3)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    scan = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15
    )

    scan = cv2.medianBlur(scan, 3)

    return scan


def decide(detection: dict) -> dict:
    """
    Stage 5:
    Produce the automatic decision and the final readable scan.
    """

    if not detection["found"]:
        return {
            "success": False,
            "corners": 0,
            "scan": None,
            "message": "Document not detected",
        }

    scan = enhance_readability(detection["warped"])

    return {
        "success": True,
        "corners": 4,
        "scan": scan,
        "message": "Document successfully scanned",
    }
