import fitz  # PyMuPDF
import requests
from tempfile import NamedTemporaryFile

def extract_text_from_pdf(file_url):
    response = requests.get(file_url)
    with NamedTemporaryFile(suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_file.flush()
        doc = fitz.open(tmp_file.name)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
