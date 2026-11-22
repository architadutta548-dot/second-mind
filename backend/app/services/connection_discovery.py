
from collections import defaultdict

from app.services.concept_extractor import extract_concepts


def discover_cross_memory_connections(memories):
    """
    Find concepts that connect different memories.

    Shared concepts are observed connections.
    They are not automatically proof of a meaningful relationship.
    """

    concept_memories = defaultdict(list)

    # Collect concepts from every memory
    for memory in memories:

        text = f"{memory.title}. {memory.content}"
        concepts = extract_concepts(text)

        for concept in set(concepts):
            concept_memories[concept].append({
                "memory_id": memory.id,
                "memory_title": memory.title,
                "category": memory.category or "general"
            })

    connections = []

    # Find concepts appearing in multiple memories
    for concept, records in concept_memories.items():

        if len(records) < 2:
            continue

        connections.append({
            "concept": concept,
            "relationship": "shared_across_memories",
            "evidence_type": "observed",
            "memory_count": len(records),
            "memories": records
        })

    connections.sort(
        key=lambda item: item["memory_count"],
        reverse=True
    )

    return {
        "total_connections": len(connections),
        "connections": connections
    }
