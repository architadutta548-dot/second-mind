
def evaluate_hypotheses(verification_data):
    """
    Evaluate the quality of generated hypotheses
    using their available supporting evidence.
    """

    evaluations = []

    for result in verification_data["results"]:

        observations = result["observations_found"]

        # Evaluate evidence strength
        if result["evidence_check"] and observations >= 3:
            evidence_strength = "strong"

        elif result["evidence_check"] and observations >= 2:
            evidence_strength = "moderate"

        elif result["evidence_check"]:
            evidence_strength = "limited"

        else:
            evidence_strength = "insufficient"

        # Calculate a simple evidence score
        evidence_score = min(observations / 5, 1.0) * 100

        evaluations.append({
            "hypothesis": result["hypothesis"],
            "verification_status": result["status"],
            "evidence_strength": evidence_strength,
            "evidence_score": round(evidence_score, 2),
            "observations_found": observations,
            "recommendation": (
                "Collect more independent evidence."
                if observations < 3
                else "Review the evidence for possible confirmation."
            )
        })

    return {
        "total_evaluated": len(evaluations),
        "evaluations": evaluations,
        "evaluation_note": (
            "Scores represent evidence quantity, not scientific "
            "probability or truth."
        )
    }
