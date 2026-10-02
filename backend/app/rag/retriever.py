import re
from collections import Counter


STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "about", "what",
    "which", "does", "have", "has", "are", "was", "were", "into", "your",
    "how", "why", "tell", "their", "they", "you", "al", "not",
}


def _tokens(text: str) -> list[str]:
    """Tokenize evidence for lightweight local retrieval."""
    return [
        token
        for token in re.findall(r"[a-zA-Z0-9+#.-]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    ]


def retrieve_with_scores(
    query: str,
    documents: list[str],
    top_k: int = 5,
) -> list[tuple[float, str]]:
    """Return ranked evidence using a transparent overlap score.

    This keeps the first release dependency-light and fully local. The function
    boundary is intentionally compatible with a future embedding/vector store.
    """
    query_counts = Counter(_tokens(query))
    query_terms = set(query_counts)

    scored: list[tuple[float, str]] = []
    for document in documents:
        document_counts = Counter(_tokens(document))
        overlap = query_terms & set(document_counts)
        if not overlap:
            continue

        # WHY: Reward unique query-term coverage while mildly rewarding repetition.
        score = sum(1.0 + min(document_counts[token], 3) * 0.1 for token in overlap)
        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:top_k]


def retrieve(query: str, documents: list[str], top_k: int = 5) -> list[str]:
    """Return only the ranked document text."""
    return [document for _, document in retrieve_with_scores(query, documents, top_k)]
