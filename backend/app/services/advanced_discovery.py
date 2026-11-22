
from app.services.concept_extractor import extract_concepts

from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity
)


def discover_advanced_connections(
    memories,
    similarity_threshold=0.65
):
    """
    Discover and rank potential connections between memories
    using concepts, semantic similarity and knowledge domains.

    Scores are experimental ranking signals,
    not probabilities or scientific confidence.
    """

    memory_data = []

    # Prepare memory information
    for memory in memories:

        text = f"{memory.title}. {memory.content}"

        concepts = set(extract_concepts(text))

        vector = memory.embedding

        if vector is None:
            vector = generate_embedding(text)

        memory_data.append({
            "id": memory.id,
            "title": memory.title,
            "category": memory.category or "general",
            "concepts": concepts,
            "embedding": vector
        })

    discoveries = []

    # Compare every pair of memories
    for i in range(len(memory_data)):

        for j in range(i + 1, len(memory_data)):

            memory_a = memory_data[i]
            memory_b = memory_data[j]

            shared_concepts = sorted(
                memory_a["concepts"].intersection(
                    memory_b["concepts"]
                )
            )

            all_concepts = (
                memory_a["concepts"].union(
                    memory_b["concepts"]
                )
            )

            if all_concepts:
                concept_overlap = (
                    len(shared_concepts) / len(all_concepts)
                )
            else:
                concept_overlap = 0.0

            similarity = cosine_similarity(
                memory_a["embedding"],
                memory_b["embedding"]
            )

            cross_domain = (
                memory_a["category"] != memory_b["category"]
            )

            # Experimental ranking score
            discovery_score = (
                similarity * 50
                + concept_overlap * 30
                + (20 if cross_domain else 0)
            )

            # Keep potentially interesting connections
            if (
                similarity >= similarity_threshold
                or shared_concepts
            ):

                discoveries.append({
                    "memory_a": {
                        "id": memory_a["id"],
                        "title": memory_a["title"],
                        "category": memory_a["category"]
                    },

                    "memory_b": {
                        "id": memory_b["id"],
                        "title": memory_b["title"],
                        "category": memory_b["category"]
                    },

                    "shared_concepts": shared_concepts,

                    "semantic_similarity": round(
                        similarity, 4
                    ),

                    "concept_overlap": round(
                        concept_overlap, 4
                    ),

                    "cross_domain": cross_domain,

                    "discovery_score": round(
                        discovery_score, 2
                    ),

                    "evidence_type": "combined_discovery_signals",

                    "status": "candidate",

                    "verification_required": True
                })

    discoveries.sort(
        key=lambda item: item["discovery_score"],
        reverse=True
    )

    return {
        "total_memories_analyzed": len(memory_data),

        "total_discoveries": len(discoveries),

        "similarity_threshold": similarity_threshold,

        "discoveries": discoveries,

        "discovery_note": (
            "Scores rank potential connections using "
            "semantic similarity, concept overlap and "
            "category differences. They do not represent "
            "scientific probability or proven relationships."
        )
    }
