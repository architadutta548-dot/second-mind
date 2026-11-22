
def validate_connections(connections):
    """
    Validate discovered connections using available evidence.

    This is an experimental evidence checker.
    It does not establish scientific truth.
    """

    validated_connections = []

    for connection in connections:

        evidence_type = connection.get(
            "evidence_type", "unknown"
        )

        evidence_count = connection.get(
            "evidence_count", 0
        )

        similarity_score = connection.get(
            "similarity_score"
        )

        status = "insufficient"
        explanation = "Not enough evidence is available."

        # Check observed relationships
        if evidence_type == "observed":

            if evidence_count >= 3:
                status = "supported"
                explanation = (
                    "The relationship appears in at least "
                    "three distinct supporting memories."
                )

            elif evidence_count >= 2:
                status = "needs_review"
                explanation = (
                    "The relationship appears in two "
                    "supporting memories."
                )

            else:
                explanation = (
                    "Only one or no supporting memory was found."
                )

        # Check semantic similarity
        elif evidence_type == "embedding_similarity":

            if similarity_score is not None:

                if similarity_score >= 0.80:
                    status = "needs_review"
                    explanation = (
                        "High semantic similarity was detected. "
                        "Manual review is still required."
                    )

                elif similarity_score >= 0.65:
                    status = "needs_review"
                    explanation = (
                        "Moderate semantic similarity was detected. "
                        "More evidence is needed."
                    )

                else:
                    explanation = (
                        "Similarity is below the experimental "
                        "review threshold."
                    )

        validated_connections.append({
            "connection": connection,
            "validation_status": status,
            "explanation": explanation,
            "verification_required": status != "supported"
        })

    return {
        "total_connections_checked": len(validated_connections),
        "supported": sum(
            1 for item in validated_connections
            if item["validation_status"] == "supported"
        ),
        "needs_review": sum(
            1 for item in validated_connections
            if item["validation_status"] == "needs_review"
        ),
        "insufficient": sum(
            1 for item in validated_connections
            if item["validation_status"] == "insufficient"
        ),
        "results": validated_connections,
        "validation_note": (
            "These labels describe available internal evidence, "
            "not scientific certainty or universal truth."
        )
    }
