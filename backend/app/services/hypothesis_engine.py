def generate_hypotheses(pattern_data):
    """
    Generate candidate hypotheses from discovered patterns.
    These are suggestions, not verified discoveries.
    """

    hypotheses = []

    # Generate hypotheses from repeated connections
    for connection in pattern_data["repeated_connections"]:
        concept_a = connection["concept_a"]
        concept_b = connection["concept_b"]
        frequency = connection["frequency"]

        hypotheses.append({
            "hypothesis": (
                f"{concept_a} may be meaningfully related to {concept_b}."
            ),
            "supporting_observations": frequency,
            "evidence": [
                f"Both concepts appeared together in {frequency} memories."
            ],
            "status": "candidate",
            "verification_required": True
        })

    # Generate hypotheses from repeated concepts
    for item in pattern_data["repeated_concepts"]:
        concept = item["concept"]

        hypotheses.append({
            "hypothesis": (
                f"{concept} may be an important recurring theme "
                "in the stored knowledge."
            ),
            "supporting_observations": item["frequency"],
            "evidence": [
                f"Found in {item['frequency']} different memories."
            ],
            "status": "candidate",
            "verification_required": True
        })

    return {
        "total_hypotheses": len(hypotheses),
        "hypotheses": hypotheses
    }