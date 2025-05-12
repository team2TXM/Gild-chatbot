import pymupdf
import re
import pandas as pd
import yfinance as yf
import os

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




# Define sectors and ticker symbols
SECTOR_COMPANIES = {
    "Defense": [
        "LMT", "RTX", "NOC", "GD", "HII", "BA", "TDG", "CW", "LHX", "AXON"
    ],
    "Technology": [
        "AAPL", "MSFT", "GOOGL", "META", "NVDA", "ORCL", "IBM", "AMD", "INTC", "CRM"
    ],
    "Agriculture": [
        "ADM", "BG", "DE", "CF", "MOS", "FMC", "TSN", "CTVA", "AGCO", "SMG"
    ],
    "Oil & Gas": [
        "XOM", "CVX", "COP", "EOG", "OXY", "HES", "DVN", "KMI"
    ]
}

def fetch_market_data(start_date="2022-01-01", end_date=None, interval="1mo"):
    """
    Fetch historical stock price data for selected companies across sectors.
    """
    all_data = []

    for sector, tickers in SECTOR_COMPANIES.items():
        for ticker in tickers:
            print(f"Fetching {ticker} from {sector}...")
            try:
                data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
                data.reset_index(inplace=True)
                data["Ticker"] = ticker
                data["Sector"] = sector
                all_data.append(data)
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

    if not all_data:
        return None

    df = pd.concat(all_data, ignore_index=True)
    
    # Save to CSV
    save_dir = "/workspaces/Gild-chatbot/data"
    os.makedirs(save_dir, exist_ok=True)
    csv_path = os.path.join(save_dir, "market_data.csv")
    df.to_csv(csv_path, index=False)

    return df