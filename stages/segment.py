import cv2
import numpy as np


def segment(image: np.ndarray) -> np.ndarray:
    """
    Stage 2:
    Segment the document from the background with Otsu thresholding.
    """

    blurred = cv2.GaussianBlur(image, (7, 7), 0)

    _, mask = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return mask
