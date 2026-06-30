import cv2
import numpy as np


CORNER_NAMES = ["TL", "TR", "BR", "BL"]
CORNER_COLORS = [(0, 220, 0), (0, 180, 255), (0, 0, 255), (255, 120, 0)]


def order_corners(pts: np.ndarray) -> np.ndarray:
    pts = pts.reshape(4, 2).astype(np.float32)

    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()

    return np.array([
        pts[np.argmin(s)],   # TL
        pts[np.argmin(d)],   # TR
        pts[np.argmax(s)],   # BR
        pts[np.argmax(d)],   # BL
    ], dtype=np.float32)


def quad_from_contour(cnt: np.ndarray) -> np.ndarray:
    peri = cv2.arcLength(cnt, True)
    for eps in (0.02, 0.03, 0.05, 0.08):
        approx = cv2.approxPolyDP(cnt, eps * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            return approx.reshape(4, 2).astype(np.float32)

    hull = cv2.convexHull(cnt)
    peri = cv2.arcLength(hull, True)
    for eps in (0.02, 0.03, 0.05, 0.08):
        approx = cv2.approxPolyDP(hull, eps * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2).astype(np.float32)

    return cv2.boxPoints(cv2.minAreaRect(cnt)).astype(np.float32)


def find_document_contour(
    mask: np.ndarray,
    min_area_frac: float = 0.10
) -> np.ndarray:
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    img_area = mask.shape[0] * mask.shape[1]

    best = None
    best_area = 0.0

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < min_area_frac * img_area:
            continue

        if area > best_area:
            best = cnt
            best_area = area

    if best is None:
        return None

    return quad_from_contour(best)


def warp_document(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    tl, tr, br, bl = corners

    top_w = np.linalg.norm(tr - tl)
    bottom_w = np.linalg.norm(br - bl)
    left_h = np.linalg.norm(bl - tl)
    right_h = np.linalg.norm(br - tr)

    out_w = int(max(top_w, bottom_w))
    out_h = int(max(left_h, right_h))

    dst = np.float32([
        [0,         0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0,         out_h - 1],
    ])

    H = cv2.getPerspectiveTransform(corners, dst)

    return cv2.warpPerspective(image, H, (out_w, out_h))


def draw_detection(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    vis = image.copy()

    cv2.polylines(
        vis,
        [corners.astype(np.int32)],
        True,
        (0, 255, 180),
        2
    )

    for pt, name, color in zip(corners, CORNER_NAMES, CORNER_COLORS):
        center = (int(pt[0]), int(pt[1]))
        cv2.circle(vis, center, 12, color, -1)
        cv2.putText(
            vis,
            name,
            (center[0] + 14, center[1] - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    return vis


def detect(clean_mask: np.ndarray, image: np.ndarray) -> dict:
    """
    Stage 4:
    Detect the document and correct its perspective.
    """

    quad = find_document_contour(clean_mask)

    if quad is None:
        return {
            "found": False,
            "corners": None,
            "warped": None,
            "visualization": image.copy(),
        }

    corners = order_corners(quad)
    warped = warp_document(image, corners)
    visualization = draw_detection(image, corners)

    return {
        "found": True,
        "corners": corners,
        "warped": warped,
        "visualization": visualization,
    }
