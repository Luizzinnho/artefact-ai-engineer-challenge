from pathlib import Path
from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

pdf_path = DATA_DIR / "políticas_da_loja.pdf"


def load_policies():
    reader = PdfReader(pdf_path)
    page_texts = []

    for page in reader.pages:
        page_texts.append(page.extract_text() or "")

    full_text = "\n".join(page_texts)

    return full_text



text = load_policies()

print(text[-500:])

        