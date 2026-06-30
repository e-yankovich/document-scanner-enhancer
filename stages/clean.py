import cv2
import numpy as np


def keep_largest(mask: np.ndarray) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8
    )

    if num_labels <= 1:
        return mask

    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])

    result = np.zeros_like(mask)
    result[labels == largest] = 255

    return result


def clean(mask: np.ndarray) -> np.ndarray:
    """
    Stage 3:
    Clean the mask into a single solid document region.
    """

    # Kernel scales with the image so background texture and thin glare
    # bridges are removed on photos of any size.
    k = max(15, int(0.025 * min(mask.shape)) | 1)
    kernel = np.ones((k, k), np.uint8)

    # Drop the fragmented background first, open to sever thin bridges to
    # the document, then keep the document blob again.
    cleaned = keep_largest(mask)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = keep_largest(cleaned)

    return cleaned
