

import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

class ResumeMatcher:
    def __init__(self, sbert_model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(sbert_model_name)

    def extract_text_from_pdf(self, filepath):
        try:
            with fitz.open(filepath) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            return text.strip()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""

    def get_resume_embeddings(self, cv_dir):
        resume_embeddings = {}
        for filename in os.listdir(cv_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(cv_dir, filename)
                resume_text = self.extract_text_from_pdf(filepath)
                if resume_text:
                    emb = self.model.encode(resume_text, convert_to_tensor=True)
                    resume_embeddings[filename] = emb
        return resume_embeddings

    def calculate_similarity_scores(self, job_embedding, resume_embeddings):
        scores = []
        for filename, emb in resume_embeddings.items():
            sim = util.pytorch_cos_sim(job_embedding, emb).item()
            scores.append((filename, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


def match_resumes_to_jd(job_summary_text, parsed_resumes: dict):
    matcher = ResumeMatcher()
    job_embedding = matcher.model.encode(job_summary_text, convert_to_tensor=True)

    resume_embeddings = {
        filename: matcher.model.encode(text, convert_to_tensor=True)
        for filename, text in parsed_resumes.items()
    }

    similarity_scores = matcher.calculate_similarity_scores(job_embedding, resume_embeddings)
    return similarity_scores








