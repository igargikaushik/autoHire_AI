# shortlister.py
from typing import List, Tuple

def shortlist_candidates(similarity_scores: List[Tuple[str, float]], threshold: float = 0.80) -> List[str]:
    return [filename for filename, score in similarity_scores if score >= threshold]