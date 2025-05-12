import nltk
import os
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from coding.tools import fetch_market_data

def update_market_data_and_show_preview():
    df = fetch_market_data()
    if df is not None:
        print("Market data preview:")
        print(df.head())
    else:
        print("No market data retrieved.")


try:
    nltk.download('punkt')  # Download punkt tokenizer
    nltk.download('stopwords')  # Download stopwords for text cleaning
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")


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

def tokenize_and_clean(text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum()]
    words = [word for word in words if word not in stop_words]
    return words

def generate_wordcloud_from_pdf():
    from coding.agenttools import extract_pdf_content  # If it's in the same file, omit this import

    # Extract text content from the PDF
    pages = extract_pdf_content()
    full_text = " ".join(pages)

    # Tokenize and clean the extracted text
    cleaned_words = tokenize_and_clean(full_text)
    word_string = " ".join(cleaned_words)

    # Generate the TF-IDF representation of the words
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([word_string])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()
    word_tfidf = dict(zip(feature_names, tfidf_scores))

    # Create the word cloud
    wc = WordCloud(
        width=800,
        height=800,
        background_color='white',
        contour_width=1,
        contour_color='black',
        colormap='plasma',
        max_words=200
    )

    wc.generate_from_frequencies(word_tfidf)

    # Specify the hardcoded save path
    save_dir = "/workspaces/Gild-chatbot/data"  # Update this with your desired path
    os.makedirs(save_dir, exist_ok=True)

    image_path = os.path.join(save_dir, "full_wordcloud.png")

    # Save the word cloud image
    wc.to_file(image_path)

    return image_path