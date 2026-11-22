
import re
from collections import Counter


# ==========================================
# 1. TEXT NORMALIZATION
# ==========================================

STOP_WORDS = {
    "the", "is", "are", "was", "were", "a", "an",
    "and", "or", "but", "in", "on", "at", "to",
    "of", "for", "with", "by", "from", "as",
    "it", "this", "that", "these", "those",
    "be", "been", "being", "has", "have", "had",
    "will", "would", "can", "could", "may",
    "about", "into", "their", "they", "them",
    "its", "what", "which", "who", "how"
}


def extract_keywords(text: str) -> set:

    if not isinstance(text, str):
        return set()

    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b", text.lower())

    return {
        word for word in words
        if word not in STOP_WORDS
    }


# ==========================================
# 2. SOURCE COMPARISON
# ==========================================

def compare_sources(sources: list) -> dict:

    if not isinstance(sources, list) or not sources:
        return {
            "status": "invalid_sources",
            "message": "At least one source is required.",
            "comparisons": []
        }

    valid_sources = []

    for source in sources:

        if not isinstance(source, dict):
            continue

        title = source.get("title", "")
        snippet = source.get("snippet", "")
        url = source.get("url", "")

        if not all(
            isinstance(value, str) and value.strip()
            for value in [title, snippet, url]
        ):
            continue

        valid_sources.append({
            "title": title.strip(),
            "snippet": snippet.strip(),
            "url": url.strip(),
            "source_domain": source.get("source_domain", "")
        })

    if not valid_sources:
        return {
            "status": "invalid_sources",
            "message": "No valid sources were provided.",
            "comparisons": []
        }

    keyword_sets = [
        extract_keywords(source["title"] + " " + source["snippet"])
        for source in valid_sources
    ]

    keyword_counts = Counter()

    for keywords in keyword_sets:
        keyword_counts.update(keywords)

    shared_keywords = [
        {
            "keyword": keyword,
            "source_count": count
        }
        for keyword, count in keyword_counts.most_common()
        if count >= 2
    ]

    comparisons = []

    for index, source in enumerate(valid_sources):

        unique_keywords = keyword_sets[index] - set(
            keyword_counts.keys()
        )

        comparisons.append({
            "title": source["title"],
            "source_domain": source["source_domain"],
            "url": source["url"],
            "snippet": source["snippet"],
            "keyword_count": len(keyword_sets[index]),
            "distinctive_keywords": sorted(unique_keywords)
        })

    return {
        "status": "comparison_completed",
        "total_sources": len(valid_sources),
        "shared_topics": shared_keywords,
        "comparisons": comparisons,
        "analysis_note": (
            "This is a keyword-based comparison of search snippets. "
            "Shared keywords indicate possible topic overlap, not "
            "verified agreement between sources."
        )
    }
