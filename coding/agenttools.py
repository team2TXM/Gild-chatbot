from coding.tools import load_pdf, extract_text_by_page

pdf_path = "/kaggle/input/ukr-rus/ukr_rus.pdf"
doc = load_pdf(pdf_path)
df = extract_text_by_page(doc, max_pages=len(doc))
