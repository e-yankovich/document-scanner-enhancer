# Document Scanner & Enhancer

A Computer Vision pipeline that turns an ordinary phone photo of a paper
document into a clean, upright, readable scan — the same job a mobile
document-scanner app does, built from classic OpenCV techniques.

University team course project, "Detect a document, correct its perspective, and improve readability."*

## What it does and why

Photographing a document by hand almost never gives a flat, front-facing page:
the sheet is rotated, distorted by perspective (a trapezoid instead of a
rectangle), lit unevenly and surrounded by a distracting background such as a
wooden table. This project automatically:

1. **finds** the document and its four corners in the photo,
2. **corrects the perspective** so the page becomes a flat rectangle,
3. **improves readability** with a scanner-style black-and-white output, and
4. produces an **automatic decision** (was a document found and scanned?).

The system is fully automatic — no manual cropping or corner picking — and saves
every intermediate stage so the process is transparent and reproducible.

## Pipeline

```
image → enhance → segment → clean → detect → decide
```

| Stage   | What it does                                              | Key methods |
|---------|-----------------------------------------------------------|-------------|
| Enhance | Normalise lighting, reduce noise, go grayscale            | gamma, CLAHE, bilateral filter |
| Segment | Separate the sheet from the background                    | Otsu thresholding |
| Clean   | Reduce the mask to one solid document silhouette          | connected components, morphological opening |
| Detect  | Locate the 4 corners and correct perspective              | contours, approxPolyDP, perspective warp |
| Decide  | Output the decision + final readable scan                 | pass/fail flag, adaptive threshold |

Each stage is a single function so the pipeline is easy to follow and each
member's contribution stays clearly separated.

## Project structure

```
document-scanner-enhancer/
├── data/              # input test images
├── output/            # per-image results
├── stages/
│   ├── enhance.py
│   ├── segment.py
│   ├── clean.py
│   ├── detect.py
│   └── decide.py
├── pipeline.py        # runs all five stages on every image in data/
├── report/            # project report
├── requirements.txt
└── README.md
```

## Setup & usage

```bash
pip install -r requirements.txt
python pipeline.py
```

Put your test photos (`.jpg`, `.jpeg`, `.png`) in `data/`, then run the command
above. For each image, `pipeline.py` writes a numbered record to
`output/<image_name>/`:

| File              | Content |
|-------------------|---------|
| `01_original.jpg` | input photo |
| `02_enhanced.jpg` | after Enhance |
| `03_mask.jpg`     | segmentation mask |
| `04_clean.jpg`    | cleaned document silhouette |
| `05_detection.jpg`| detected corners drawn on the original |
| `06_warped.jpg`   | perspective-corrected original (colour) |
| `07_scan.jpg`     | final readable scanner-style output |
| `decision.txt`    | automatic decision (message, success, corner count) |

## Assumptions

Works best on a single, mostly flat document that is **brighter** than a
**darker, contrasting** background. See `report/report.pdf` (Failure cases) for
known limitations.

## Team

| Member             | Role                              | Stages |
|--------------------|-----------------------------------|--------|
| Volha Platnitskaya | Image Processing & Morphology     | Enhance, Segment, Clean |
| Evgeniya Yankovich | Lead CV Engineer (integration)    | Detect, Decide, Pipeline |
