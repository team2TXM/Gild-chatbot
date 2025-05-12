from coding.tools import load_pdf, extract_text_by_page

def extract_pdf_content():
    from PyPDF2 import PdfReader

    try:
        pdf_path = "/workspaces/Gild-chatbot/data/ukr_rus.pdf"  # Replace with your actual path
        reader = PdfReader(pdf_path)

        print(f"PDF has {len(reader.pages)} pages.")

        paginated_content = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"Extracted page {i+1}: {len(text) if text else 0} characters")
            paginated_content.append(text if text else "[Empty Page]")

        return paginated_content

    except Exception as e:
        print(f"Error while extracting PDF content: {e}")
        return ["I am sorry, I encountered an error trying to extract the content from the PDF file. Please try again."]

