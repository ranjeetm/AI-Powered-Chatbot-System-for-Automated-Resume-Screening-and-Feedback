import fitz
import pytesseract

from pdf2image import convert_from_path
from pathlib import Path


def extract_text_from_pdf(
    pdf_path
):

    extracted_text = ""

    try:

        # --------------------------------
        # DIRECT PDF TEXT EXTRACTION
        # --------------------------------

        pdf_document = fitz.open(
            pdf_path
        )

        total_pages = len(
            pdf_document
        )

        for page in pdf_document:

            extracted_text += (
                page.get_text()
                + "\n"
            )

        pdf_document.close()

        # --------------------------------
        # RETURN DIRECT TEXT IF AVAILABLE
        # --------------------------------

        if extracted_text.strip():

            return {

                "file_name":
                    Path(pdf_path).name,

                "text":
                    extracted_text.strip(),

                "pages":
                    total_pages
            }

        # --------------------------------
        # OCR FALLBACK
        # --------------------------------

        extracted_text = ""

        images = convert_from_path(
            pdf_path
        )

        for image in images:

            text = pytesseract.image_to_string(
                image
            )

            extracted_text += (
                text + "\n"
            )

        return {

            "file_name":
                Path(pdf_path).name,

            "text":
                extracted_text.strip(),

            "pages":
                len(images)
        }

    except Exception as e:

        print(
            f"\nPDF PARSER ERROR: {e}"
        )

        return {

            "file_name":
                Path(pdf_path).name,

            "error":
                str(e)
        }