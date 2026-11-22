
import re


# Known concepts used by Second Mind.
KNOWN_CONCEPTS = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Neural Networks",
    "Pattern Recognition",
    "Data",
    "Computer Science",
    "Cognitive AI",
    "Knowledge Graph",
    "Semantic Search",
    "Natural Language Processing"
]


def extract_concepts(text: str) -> list:
    """
    Extract known concepts regardless of capitalization.
    """

    if not text:
        return []

    concepts = []
    text_lower = text.lower()

    for concept in KNOWN_CONCEPTS:
        pattern = (
            r"\b" + re.escape(concept.lower()) + r"\b"
        )

        if re.search(pattern, text_lower):
            concepts.append(concept)

    return concepts
