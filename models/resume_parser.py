import os
import fitz#PyMuPDF
import re

CV_DIR = "data/CVs"  


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def clean_resume_text(text: str) -> str:
    """Cleans extracted resume text using basic regex."""
    text = re.sub(r'\s+', ' ', text)  # remo extra whitespaces/newlines
    return text.strip()


def extract_and_clean_text(pdf_path: str) -> str:
    """Extracts and cleans text from a given PDF."""
    raw_text = extract_text_from_pdf(pdf_path)
    return clean_resume_text(raw_text)


def extract_all_resumes_texts(cv_dir: str = CV_DIR) -> dict:
    """
    Extracts and cleans text from all resumes in a given folder.

    Returns:
        dict: A mapping of {filename: cleaned_text}
    """
    resume_texts = {}
    for filename in os.listdir(cv_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(cv_dir, filename)
            clean_text = extract_and_clean_text(file_path)
            resume_texts[filename] = clean_text
    return resume_texts

def parse_resume(cv_dir: str = CV_DIR) -> dict:
    return extract_all_resumes_texts(cv_dir)

# eg usage
if __name__ == "__main__":
    all_resumes = extract_all_resumes_texts()
    print(f"Extracted {len(all_resumes)} resumes.")
    # Print a sample
    for name, text in list(all_resumes.items())[:1]:
        print(f"\n{name}:\n{text[:500]}...")






