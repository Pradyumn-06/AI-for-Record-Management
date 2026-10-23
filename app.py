import os
import uuid

from flask import Flask, render_template, request, send_from_directory
from database import init_db, add_record, search_records, get_all_records
from ai_utils import (
    extract_text_from_file,
    classify_record,
    extract_department,
    extract_date
)

import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "bmp", "tiff", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded"

        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        if not allowed_file(file.filename):
            return "File type not allowed"

        original_name = file.filename
        extension = original_name.rsplit(".", 1)[1].lower()
        saved_name = f"{uuid.uuid4().hex}.{extension}"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
        file.save(filepath)

        text = extract_text_from_file(filepath)
        record_type, confidence = classify_record(text)
        department = extract_department(text)
        date_found = extract_date(text)

        add_record(
            filename=saved_name,
            original_name=original_name,
            record_type=record_type,
            confidence=confidence,
            extracted_text=text,
            department=department
        )

        return render_template(
            "upload.html",
            success=True,
            original_name=original_name,
            record_type=record_type,
            confidence=confidence,
            department=department,
            date_found=date_found,
            text_preview=text[:800]
        )

    return render_template("upload.html", success=False)


@app.route("/download/<path:filename>")
def download(filename):
    name = request.args.get("name") or filename
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename,
        as_attachment=True, download_name=name
    )

@app.route("/records")
def records():
    query = request.args.get("q", "")

    if query:
        results = search_records(query)
    else:
        results = get_all_records()

    return render_template("records.html", records=results, query=query)


if __name__ == "__main__":
    app.run(debug=True)