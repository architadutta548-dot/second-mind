
from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity
)


def discover_semantic_connections(memories, threshold=0.65):
    """
    Discover potentially related memories using
    semantic similarity.

    Reuse stored embeddings whenever available.
    Missing embeddings are generated automatically.
    """

    memory_vectors = []

    # Get embeddings for each memory
    for memory in memories:

        vector = memory.embedding

        # Generate an embedding only if one is missing
        if vector is None:
            text = f"{memory.title}. {memory.content}"
            vector = generate_embedding(text)

        memory_vectors.append({
            "id": memory.id,
            "title": memory.title,
            "category": memory.category or "general",
            "embedding": vector
        })

    connections = []

    # Compare every pair of memories
    for i in range(len(memory_vectors)):

        for j in range(i + 1, len(memory_vectors)):

            memory_a = memory_vectors[i]
            memory_b = memory_vectors[j]

            similarity = cosine_similarity(
                memory_a["embedding"],
                memory_b["embedding"]
            )

            if similarity >= threshold:

                connections.append({
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
                    "similarity_score": round(similarity, 4),
                    "relationship": "potential_semantic_connection",
                    "evidence_type": "embedding_similarity",
                    "verification_required": True
                })

    # Sort by highest similarity first
    connections.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return {
        "total_memories_analyzed": len(memories),
        "total_semantic_connections": len(connections),
        "similarity_threshold": threshold,
        "connections": connections
    }
