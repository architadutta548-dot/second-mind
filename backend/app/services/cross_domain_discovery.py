
from collections import defaultdict

from app.services.concept_extractor import extract_concepts


def discover_cross_domain_connections(memories):
    """
    Find concepts that appear across multiple
    knowledge categories.
    """

    concept_domains = defaultdict(list)

    for memory in memories:
        text = f"{memory.title}. {memory.content}"
        concepts = extract_concepts(text)

        category = memory.category or "general"

        for concept in set(concepts):
            concept_domains[concept].append({
                "memory_id": memory.id,
                "memory_title": memory.title,
                "category": category
            })

    connections = []

    for concept, records in concept_domains.items():

        categories = sorted({
            record["category"]
            for record in records
        })

        if len(categories) >= 2:
            connections.append({
                "concept": concept,
                "categories_connected": categories,
                "number_of_categories": len(categories),
                "supporting_memories": records
            })

    connections.sort(
        key=lambda item: item["number_of_categories"],
        reverse=True
    )

    return {
        "total_cross_domain_connections": len(connections),
        "connections": connections
    }
