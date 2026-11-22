
import re
from collections import defaultdict

from app.services.concept_extractor import extract_concepts
from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity
)

SIMILARITY_THRESHOLD = 0.75

RELATIONSHIP_PATTERNS = [
    "is used in",
    "are used in",
    "uses",
    "use",
    "supports",
    "support",
    "helps",
    "help",
    "enables",
    "enable",
    "consists of",
    "includes",
    "contains",
    "is part of",
    "are part of",
    "is a type of",
    "are a type of"
]


def detect_explicit_relationships(memory, query_concepts):

    explicit_pairs = []

    # Examine title and content separately.
    text = (
        memory["title"] + ". " +
        memory["content"]
    )

    sentences = re.split(r"[.!?;]+", text)

    for sentence in sentences:

        sentence_lower = sentence.lower()

        concepts = sorted(
            set(extract_concepts(sentence)).intersection(
                query_concepts
            )
        )

        # Find the positions of concepts in this sentence.
        positions = []

        for concept in concepts:

            position = sentence_lower.find(
                concept.lower()
            )

            if position != -1:
                positions.append({
                    "concept": concept,
                    "start": position,
                    "end": position + len(concept)
                })

        positions.sort(key=lambda item: item["start"])

        # Check relationship wording between adjacent concepts.
        for i in range(len(positions) - 1):

            first = positions[i]
            second = positions[i + 1]

            between = sentence_lower[
                first["end"]:second["start"]
            ]

            if any(
                pattern in between
                for pattern in RELATIONSHIP_PATTERNS
            ):

                pair = tuple(sorted([
                    first["concept"],
                    second["concept"]
                ]))

                explicit_pairs.append(pair)

    return explicit_pairs


def perform_advanced_reasoning(query, memories):

    if not query or not query.strip():
        return {
            "status": "invalid_query",
            "message": "Query cannot be empty."
        }

    if not memories:
        return {
            "status": "no_evidence",
            "candidate_insights": []
        }

    query_concepts = set(extract_concepts(query))

    memory_data = []

    for memory in memories:

        memory_data.append({
            "memory_id": memory.get("id"),
            "title": memory.get("title", ""),
            "content": memory.get("content", ""),
            "category": memory.get("category", "general")
        })

    # Extract concepts from every memory.
    for memory in memory_data:

        text = (
            memory["title"] + ". " +
            memory["content"]
        )

        memory["concepts"] = set(
            extract_concepts(text)
        )

    # Detect direct concept co-occurrence.
    direct_evidence = defaultdict(list)

    for memory in memory_data:

        relevant_concepts = sorted(
            memory["concepts"].intersection(
                query_concepts
            )
        )

        for i in range(len(relevant_concepts)):

            for j in range(i + 1, len(relevant_concepts)):

                pair = (
                    relevant_concepts[i],
                    relevant_concepts[j]
                )

                direct_evidence[pair].append(
                    memory["memory_id"]
                )

    # Detect explicit relationships sentence by sentence.
    explicit_relationships = defaultdict(list)

    for memory in memory_data:

        detected_pairs = detect_explicit_relationships(
            memory,
            query_concepts
        )

        for pair in detected_pairs:

            explicit_relationships[pair].append(
                memory["memory_id"]
            )

    connections = []

    # Compare memories pair by pair.
    for i in range(len(memory_data)):

        for j in range(i + 1, len(memory_data)):

            memory_a = memory_data[i]
            memory_b = memory_data[j]

            text_a = (
                memory_a["title"] + " " +
                memory_a["content"]
            )

            text_b = (
                memory_b["title"] + " " +
                memory_b["content"]
            )

            shared_concepts = sorted(
                memory_a["concepts"].intersection(
                    memory_b["concepts"]
                )
            )

            relevant_shared = [
                concept
                for concept in shared_concepts
                if concept in query_concepts
            ]

            embedding_a = generate_embedding(text_a)
            embedding_b = generate_embedding(text_b)

            similarity = cosine_similarity(
                embedding_a,
                embedding_b
            )

            if (
                not relevant_shared
                and similarity < SIMILARITY_THRESHOLD
            ):
                continue

            # Get concepts relevant to this memory pair.
            pair_concepts = sorted(
                memory_a["concepts"].union(
                    memory_b["concepts"]
                ).intersection(query_concepts)
            )

            supporting_ids = set()
            explicit_ids = set()

            for x in range(len(pair_concepts)):

                for y in range(x + 1, len(pair_concepts)):

                    pair = (
                        pair_concepts[x],
                        pair_concepts[y]
                    )

                    supporting_ids.update(
                        direct_evidence.get(pair, [])
                    )

                    explicit_ids.update(
                        explicit_relationships.get(pair, [])
                    )

            supporting_ids = sorted(supporting_ids)
            explicit_ids = sorted(explicit_ids)

            observations = len(explicit_ids)

            # Evaluate explicit evidence quantity.
            if observations >= 3:
                evidence_strength = "strong"

            elif observations == 2:
                evidence_strength = "moderate"

            elif observations == 1:
                evidence_strength = "limited"

            else:
                evidence_strength = "insufficient"

            # Classify the evidence.
            if explicit_ids:
                verification_status = "explicit_relationship"

            elif supporting_ids:
                verification_status = "cooccurrence_only"

            elif relevant_shared:
                verification_status = "shared_concept_only"

            else:
                verification_status = "semantic_candidate"

            connections.append({
                "memory_ids": [
                    memory_a["memory_id"],
                    memory_b["memory_id"]
                ],
                "shared_concepts": shared_concepts,
                "query_relevant_shared_concepts": relevant_shared,
                "supporting_memory_ids": supporting_ids,
                "explicit_relationship_memory_ids": explicit_ids,
                "observations_found": observations,
                "semantic_similarity": round(
                    similarity, 4
                ),
                "verification_status": verification_status,
                "evidence_strength": evidence_strength,
                "verification_required": True
            })

    candidate_insights = []

    for connection in connections:

        if connection["query_relevant_shared_concepts"]:

            statement = (
                "Shared query concepts: " +
                ", ".join(
                    connection["query_relevant_shared_concepts"]
                )
            )

        else:

            statement = (
                "Semantically similar memories detected."
            )

        candidate_insights.append({
            "statement": statement,
            "based_on_memory_ids": connection["memory_ids"],
            "supporting_memory_ids": connection["supporting_memory_ids"],
            "explicit_relationship_memory_ids":
                connection["explicit_relationship_memory_ids"],
            "observations_found": connection["observations_found"],
            "semantic_similarity": connection["semantic_similarity"],
            "verification_status": connection["verification_status"],
            "evidence_strength": connection["evidence_strength"],
            "verification_required": True
        })

    return {
        "status": (
            "connections_found"
            if connections
            else "no_connections_found"
        ),
        "query": query,
        "reasoning_type": "advanced_multi_memory_reasoning",
        "total_memories_analyzed": len(memory_data),
        "total_connections_found": len(connections),
        "candidate_insights": candidate_insights,
        "verification_note": (
            "Explicit relationships are detected using "
            "recognized relationship phrases within individual "
            "sentences. This is a rule-based check, not proof "
            "of scientific truth."
        )
    }
