
from app.services.concept_extractor import extract_concepts

from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity
)


def expand_knowledge(
    new_memory,
    existing_memories,
    similarity_threshold=0.65
):
    """
    Expand knowledge using:
    1. Shared concept detection
    2. Semantic similarity between memories

    These connections are suggestions for investigation,
    not proof of meaningful relationships.
    """

    new_text = f"{new_memory.title}. {new_memory.content}"

    new_concepts = set(extract_concepts(new_text))

    # Reuse the new memory's stored embedding
    new_vector = new_memory.embedding

    if new_vector is None:
        new_vector = generate_embedding(new_text)

    concept_connections = []
    semantic_connections = []

    for memory in existing_memories:

        if memory.id == new_memory.id:
            continue

        existing_text = f"{memory.title}. {memory.content}"

        existing_concepts = set(
            extract_concepts(existing_text)
        )

        # --------------------------------
        # 1. Shared concept detection
        # --------------------------------

        shared_concepts = sorted(
            new_concepts.intersection(existing_concepts)
        )

        if shared_concepts:

            concept_connections.append({
                "new_memory": {
                    "id": new_memory.id,
                    "title": new_memory.title
                },
                "connected_memory": {
                    "id": memory.id,
                    "title": memory.title
                },
                "shared_concepts": shared_concepts,
                "relationship": "shares_concepts",
                "evidence_type": "observed",
                "verification_required": True
            })

        # --------------------------------
        # 2. Semantic similarity detection
        # --------------------------------

        existing_vector = memory.embedding

        if existing_vector is None:
            existing_vector = generate_embedding(
                existing_text
            )

        similarity = cosine_similarity(
            new_vector,
            existing_vector
        )

        if similarity >= similarity_threshold:

            semantic_connections.append({
                "new_memory": {
                    "id": new_memory.id,
                    "title": new_memory.title
                },
                "connected_memory": {
                    "id": memory.id,
                    "title": memory.title
                },
                "similarity_score": round(similarity, 4),
                "relationship": "potential_semantic_connection",
                "evidence_type": "embedding_similarity",
                "verification_required": True
            })

    # Sort semantic connections by similarity
    semantic_connections.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return {
        "new_memory_id": new_memory.id,
        "new_concepts": sorted(new_concepts),

        "concept_connections": {
            "total": len(concept_connections),
            "connections": concept_connections
        },

        "semantic_connections": {
            "total": len(semantic_connections),
            "similarity_threshold": similarity_threshold,
            "connections": semantic_connections
        },

        "verification_note": (
            "Shared concepts and semantic similarity are "
            "signals for further investigation, not proof "
            "of meaningful relationships."
        )
    }
