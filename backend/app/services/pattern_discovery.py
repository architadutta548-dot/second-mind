from collections import Counter
from app.services.concept_extractor import extract_concepts


def discover_patterns(memories):
    """
    Find repeated concepts and relationships
    across saved memories.
    """

    concept_frequency = Counter()
    memory_connections = Counter()
    concept_memories = {}

    for memory in memories:
        text = f"{memory.title}. {memory.content}"
        concepts = extract_concepts(text)

        # Count how often each concept appears
        for concept in set(concepts):
            concept_frequency[concept] += 1

            if concept not in concept_memories:
                concept_memories[concept] = []

            concept_memories[concept].append({
                "memory_id": memory.id,
                "memory_title": memory.title
            })

        # Count concepts appearing together
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                pair = tuple(sorted([
                    concepts[i],
                    concepts[j]
                ]))

                memory_connections[pair] += 1

    repeated_concepts = [
        {
            "concept": concept,
            "frequency": frequency,
            "found_in": concept_memories[concept]
        }
        for concept, frequency in concept_frequency.items()
        if frequency > 1
    ]

    repeated_connections = [
        {
            "concept_a": pair[0],
            "concept_b": pair[1],
            "frequency": frequency
        }
        for pair, frequency in memory_connections.items()
        if frequency > 1
    ]

    return {
        "total_memories_analyzed": len(memories),
        "unique_concepts": len(concept_frequency),
        "repeated_concepts": repeated_concepts,
        "repeated_connections": repeated_connections
    }