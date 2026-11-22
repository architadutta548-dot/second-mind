
from app.services.concept_extractor import extract_concepts


def reason_about_knowledge(query, memories):
    """
    Analyze concepts and relationships using retrieved memories.
    This is experimental rule-based reasoning.
    """

    query = query.strip()

    if not query:
        return {
            "query": query,
            "status": "invalid_query",
            "message": "Please provide a question."
        }

    if not memories:
        return {
            "query": query,
            "status": "no_evidence",
            "supporting_memories": [],
            "detected_concepts": [],
            "direct_evidence": [],
            "observations": [],
            "conclusion": (
                "There is not enough stored knowledge "
                "to form a conclusion."
            )
        }

    supporting_memories = []

    for memory in memories:
        supporting_memories.append({
            "memory_id": memory.id,
            "title": memory.title,
            "content": memory.content,
            "category": memory.category or "general"
        })

    # Collect concepts from retrieved memories.
    known_concepts = set()

    for memory in supporting_memories:
        known_concepts.update(
            extract_concepts(
                memory["title"] + ". " + memory["content"]
            )
        )

    # Identify known concepts mentioned in the query.
    query_lower = query.lower()

    detected_concepts = sorted(
        [
            concept
            for concept in known_concepts
            if concept.lower() in query_lower
        ],
        key=lambda concept: query_lower.find(concept.lower())
    )

    # Find memories containing each detected concept.
    concept_evidence = {}

    for concept in detected_concepts:
        matching_memories = []

        for memory in supporting_memories:
            memory_text = (
                memory["title"] + " " + memory["content"]
            ).lower()

            if concept.lower() in memory_text:
                matching_memories.append(memory["memory_id"])

        concept_evidence[concept] = matching_memories

    # Find direct co-occurrence evidence.
    direct_evidence = []

    for memory in supporting_memories:
        memory_text = (
            memory["title"] + " " + memory["content"]
        ).lower()

        matched_concepts = [
            concept
            for concept in detected_concepts
            if concept.lower() in memory_text
        ]

        if len(matched_concepts) >= 2:
            direct_evidence.append({
                "memory_id": memory["memory_id"],
                "title": memory["title"],
                "content": memory["content"],
                "matched_concepts": matched_concepts
            })

    observations = []

    if detected_concepts:
        observations.append(
            f"{len(detected_concepts)} known concepts "
            "were identified in the query."
        )

    if direct_evidence:
        observations.append(
            f"{len(direct_evidence)} memories mention "
            "at least two detected concepts together."
        )

    elif len(detected_concepts) >= 2:
        observations.append(
            "No retrieved memory directly mentions "
            "two or more detected concepts together."
        )

    elif not detected_concepts:
        observations.append(
            "No known concepts from the retrieved memories "
            "were identified in the query."
        )

    # Generate a conclusion based on available evidence.
    if len(detected_concepts) >= 2 and direct_evidence:
        concept_names = ", ".join(detected_concepts)

        conclusion = (
            f"The stored knowledge contains direct "
            f"co-occurrence evidence for {concept_names}. "
            "These concepts appear together in at least "
            "one retrieved memory. This indicates an "
            "observed connection, but does not prove "
            "a meaningful or causal relationship."
        )

        status = "evidence_supported"

    elif len(detected_concepts) >= 2:
        conclusion = (
            "The retrieved memories mention the requested "
            "concepts, but no direct co-occurrence evidence "
            "was found. More information is needed."
        )

        status = "insufficient_evidence"

    elif len(detected_concepts) == 1:
        conclusion = (
            f"The stored knowledge contains information "
            f"about {detected_concepts[0]}, but there is "
            "not enough evidence to establish a relationship "
            "with another concept."
        )

        status = "partial_evidence"

    else:
        conclusion = (
            "The retrieved memories do not contain "
            "recognized concepts from this query. "
            "More relevant knowledge may need to be stored."
        )

        status = "no_matching_concepts"

    return {
        "query": query,
        "status": status,
        "detected_concepts": detected_concepts,
        "supporting_memories": supporting_memories,
        "concept_evidence": concept_evidence,
        "direct_evidence": direct_evidence,
        "observations": observations,
        "conclusion": conclusion,
        "reasoning_type": "general_rule_based",
        "verification_required": True,
        "reasoning_note": (
            "Direct co-occurrence is an observed pattern, "
            "not proof of causation or scientific truth."
        )
    }
