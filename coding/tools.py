import pymupdf
import re
import pandas as pd

def load_pdf(pdf_path: str):
    """
    Load a PDF document using pymupdf.
    """
    try:
        doc = pymupdf.open(pdf_path, filetype="pdf")
        return doc
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found at '{pdf_path}'")
    except Exception as e:
        raise RuntimeError(f"Error loading PDF: {e}")

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and HTML tags.
    """
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'-\s+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def extract_text_by_page(doc, max_pages: int = 40) -> pd.DataFrame:
    """
    Extract cleaned text (and tables) from each page of the PDF.
    
    Returns:
        pd.DataFrame with 'page' and 'content' columns.
    """
    results = []
    total_pages = min(len(doc), max_pages)

    for page_number in range(total_pages):
        try:
            page = doc[page_number]
            text = clean_text(page.get_text())

            # Extract tables and append to text
            tables = page.find_tables()
            for table in tables:
                df = table.to_pandas()
                text += "\nTable:\n" + df.to_string() + "\n"

            results.append({"page": page_number + 1, "content": text})

        except Exception as e:
            print(f"Error processing page {page_number}: {e}")

    return pd.DataFrame(results)
