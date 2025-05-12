from coding.tools import load_pdf, extract_text_by_page

def extract_pdf_content():
    pdf_path = "/workspaces/Gild-chatbot/data/uk_conflict_timeline.pdf"
    doc = load_pdf(pdf_path)
    if doc is None:
        return "Failed to load PDF."

    extracted = extract_text_by_page(doc, max_pages=40)
    combined_text = "\n\n".join([f"Page {entry['page']}:\n{entry['content']}" for entry in extracted])
    return combined_text[:8000] + "\n\n...[truncated]" if len(combined_text) > 8000 else combined_text
