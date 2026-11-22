
def extract_relationships(concepts):
    """
    Extract observed relationships between concepts.

    Relationships represent co-occurrence in the same
    memory, not proven causation or scientific facts.
    """

    relationships = []

    # Compare every pair of concepts
    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):

            source = concepts[i]
            target = concepts[j]

            relationships.append({
                "source": source,
                "target": target,
                "relationship": "co_occurs_in_memory",
                "evidence_type": "observed",
                "evidence_count": 1,
                "confidence": "not_assessed"
            })

    return relationships
