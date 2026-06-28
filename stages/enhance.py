import cv2
import numpy as np


def gamma_correction(image: np.ndarray, gamma: float = 1.2) -> np.ndarray:
    inv_gamma = 1.0 / gamma

    table = np.array([
        ((i / 255.0) ** inv_gamma) * 255
        for i in np.arange(256)
    ]).astype("uint8")

    return cv2.LUT(image, table)


def enhance(image: np.ndarray) -> np.ndarray:
    """
    Stage 1:
    Improve illumination and reduce noise.
    """

    image = gamma_correction(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    gray = cv2.bilateralFilter(
        gray,
        d=7,
        sigmaColor=50,
        sigmaSpace=50
    )

    return gray