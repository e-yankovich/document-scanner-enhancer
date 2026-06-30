import os

import cv2

from stages.enhance import enhance
from stages.segment import segment
from stages.clean import clean
from stages.detect import detect
from stages.decide import decide


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def run_pipeline(image_path: str, output_dir: str) -> dict:
    """
    Run the full pipeline on one image and save every stage:
    enhance -> segment -> clean -> detect -> decide.
    """

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)

    enhanced = enhance(img)
    mask = segment(enhanced)
    clean_mask = clean(mask)
    detection = detect(clean_mask, img)
    result = decide(detection)

    os.makedirs(output_dir, exist_ok=True)

    cv2.imwrite(os.path.join(output_dir, "01_original.jpg"), img)
    cv2.imwrite(os.path.join(output_dir, "02_enhanced.jpg"), enhanced)
    cv2.imwrite(os.path.join(output_dir, "03_mask.jpg"), mask)
    cv2.imwrite(os.path.join(output_dir, "04_clean.jpg"), clean_mask)
    cv2.imwrite(os.path.join(output_dir, "05_detection.jpg"), detection["visualization"])

    if detection["warped"] is not None:
        cv2.imwrite(os.path.join(output_dir, "06_warped.jpg"), detection["warped"])

    if result["scan"] is not None:
        cv2.imwrite(os.path.join(output_dir, "07_scan.jpg"), result["scan"])

    with open(os.path.join(output_dir, "decision.txt"), "w") as f:
        f.write(f"{result['message']}\n")
        f.write(f"success: {result['success']}\n")
        f.write(f"corners: {result['corners']}\n")

    return result


def main():
    images = sorted(
        f for f in os.listdir(DATA_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )

    for fname in images:
        name = os.path.splitext(fname)[0]
        image_path = os.path.join(DATA_DIR, fname)
        output_dir = os.path.join(OUTPUT_DIR, name)

        result = run_pipeline(image_path, output_dir)
        print(f"{fname}: {result['message']}")


if __name__ == "__main__":
    main()
