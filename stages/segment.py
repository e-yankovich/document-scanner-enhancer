import cv2
import numpy as np


def segment(image: np.ndarray) -> np.ndarray:
    """
    Stage 2:
    Segment the document.
    """

    adaptive = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21,
        10
    )

    adaptive = cv2.bitwise_not(adaptive)

    edges = cv2.Canny(image, 50, 150)

    mask = cv2.bitwise_or(
        adaptive,
        edges
    )

    return mask