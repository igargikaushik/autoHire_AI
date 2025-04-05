

import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

JD_PATH = "data/job_description.csv"

#SBERT model
sbert_model = SentenceTransformer("all-mpnet-base-v2")

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_key_elements(jd_text, top_n=3):
    """
    Extracts top elements based on TF-IDF weighting and SBERT embedding similarity.
    """
    jd_text = preprocess_text(jd_text)
    sentences = re.split(r'[.?!]\s+', jd_text)
    sentences = [s for s in sentences if len(s) > 10]

    if not sentences:
        return {}

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    tfidf_scores = X.sum(axis=1).A1
    ranked_indices = np.argsort(tfidf_scores)[::-1][:top_n]

    key_sentences = [sentences[i] for i in ranked_indices]
    return {
        "summary": " ".join(key_sentences),
        "top_sentences": key_sentences
    }

def summarize_all_jds(path=JD_PATH):
    """
    Summarizes all job descriptions from a CSV file.
    Assumes the file has a column 'Job_Description'.
    """
    df = pd.read_csv(path, encoding="ISO-8859-1")

    summaries = []
    for jd in df['Job Description']:
        if isinstance(jd, str):
            summary = extract_key_elements(jd)
            summaries.append(summary)
        else:
            summaries.append({"summary": "", "top_sentences": []})

    df['Summary'] = [s['summary'] for s in summaries]
    return df


#eg usage
if __name__ == "__main__":
    summarized_df = summarize_all_jds()
    print(summarized_df[['Job Description', 'Summary']].head())








