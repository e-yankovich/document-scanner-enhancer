import cv2
import numpy as np


def clean(mask: np.ndarray) -> np.ndarray:
    """
    Stage 3:
    Remove small artifacts.
    """

    kernel = np.ones((3, 3), np.uint8)

    cleaned = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    cleaned = cv2.morphologyEx(
        cleaned,
        cv2.MORPH_OPEN,
        kernel
    )

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        cleaned,
        connectivity=4
    )

    result = np.zeros_like(cleaned)

    MIN_AREA = 50

    for i in range(1, num_labels):

        if stats[i, cv2.CC_STAT_AREA] > MIN_AREA:
            result[labels == i] = 255

    return result