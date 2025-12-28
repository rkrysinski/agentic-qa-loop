import chainlit as cl

def extract_text_from_file(file: cl.File) -> str:
    # Basic text extraction for now. Can be expanded for PDF/Docx later if needed.
    # Assuming text based files for now as per simple requirements start.
    with open(file.path, "r", encoding="utf-8") as f:
        return f.read()
