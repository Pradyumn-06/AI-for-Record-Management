import os
import re

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from transformers import pipeline

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

POPPLER_PATH = r"C:\poppler\poppler-26.09.0\Library\bin"

CONFIDENCE_THRESHOLD = 40  # below this, the label is treated as "other record"

RECORD_TYPES = [
    "fee receipt",
    "invoice",
    "leave application",
    "complaint",
    "certificate",
    "report",
    "identity document",
    "other record"
]

DEPARTMENTS = [
    "accounts",
    "human resources",
    "hr",
    "examination",
    "library",
    "administration",
    "technical",
    "student affairs"
]

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)


def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        pages = convert_from_path(filepath, poppler_path=POPPLER_PATH)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page) + "\n"
        return text.strip()

    if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        image = Image.open(filepath)
        return pytesseract.image_to_string(image).strip()

    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    return ""


def classify_record(text):
    if not text:
        return "other record", 0.0

    sample_text = text[:1500]

    result = classifier(
        sample_text,
        candidate_labels=RECORD_TYPES,
        hypothesis_template="This document is a {}."
    )

    record_type = result["labels"][0]
    confidence = round(result["scores"][0] * 100, 2)

    if confidence < CONFIDENCE_THRESHOLD:
        return "other record", confidence

    return record_type, confidence


def extract_department(text):
    lower_text = text.lower()

    for department in DEPARTMENTS:
        # \b makes this match whole words only, so "hr" won't match "three"
        if re.search(r"\b" + re.escape(department) + r"\b", lower_text):
            return "HR" if department == "hr" else department.title()

    return "General"


def extract_date(text):
    patterns = [
        r"\d{2}[/-]\d{2}[/-]\d{4}",
        r"\d{4}[/-]\d{2}[/-]\d{2}"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()

    return "Not found"