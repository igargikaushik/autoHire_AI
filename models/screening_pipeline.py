from models.jd_summarizer import summarize_all_jds
from models.resume_parser import parse_resume
from models.resume_matcher import match_resumes_to_jd
from models.shortlister import shortlist_candidates
from datetime import datetime
def run_screening_pipeline(jd_path, resumes_folder, similarity_threshold=0.80):
    summarized_df = summarize_all_jds(jd_path)
    if summarized_df.empty or 'Summary' not in summarized_df or summarized_df['Summary'].dropna().empty:
        return None  

    job_summary = summarized_df['Summary'].iloc[0]
    parsed_resumes = parse_resume(resumes_folder)
    matched_results = match_resumes_to_jd(job_summary, parsed_resumes)
    shortlisted = shortlist_candidates(matched_results, threshold=similarity_threshold)

    return shortlisted
def run_single_resume_screening(jd_path, parsed_resumes, similarity_threshold=0.80):
    summarized_df = summarize_all_jds(jd_path)
    if summarized_df.empty or 'Summary' not in summarized_df or summarized_df['Summary'].dropna().empty:
        return [], {}

    job_summary = summarized_df['Summary'].iloc[0]
    similarity_scores = match_resumes_to_jd(job_summary, parsed_resumes)

    shortlisted = shortlist_candidates(similarity_scores, threshold=similarity_threshold)
    return shortlisted, dict(similarity_scores)

# Example usage
if __name__ == "__main__":
    jd_csv = "data/job_description.csv"
    cv_folder = "data/CVs"
    top_candidates = run_screening_pipeline(jd_csv, cv_folder)

    print("Shortlisted Candidates:")
    for candidate in top_candidates:
        print(candidate)



