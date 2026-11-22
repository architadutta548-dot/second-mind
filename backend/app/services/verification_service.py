
def verify_hypotheses(hypothesis_data, pattern_data):
    """
    Check whether candidate hypotheses are supported
    by patterns found in stored memories.

    This verifies internal evidence, not universal truth.
    """

    verified_results = []

    repeated_concepts = {
        item["concept"]: item
        for item in pattern_data["repeated_concepts"]
    }

    repeated_connections = {
        (item["concept_a"], item["concept_b"]): item
        for item in pattern_data["repeated_connections"]
    }

    for item in hypothesis_data["hypotheses"]:
        statement = item["hypothesis"]

        result = {
            "hypothesis": statement,
            "status": "insufficient_evidence",
            "evidence_check": False,
            "observations_found": 0,
            "explanation": ""
        }

        matched = False

        # Check recurring concepts
        for concept, data in repeated_concepts.items():
            if concept in statement:
                result["observations_found"] = data["frequency"]
                result["evidence_check"] = (
                    data["frequency"] == item["supporting_observations"]
                )
                matched = result["evidence_check"]

                result["explanation"] = (
                    f"{concept} was found in "
                    f"{data['frequency']} different memories."
                )
                break

        # Check repeated concept connections
        if not matched:
            for (concept_a, concept_b), data in repeated_connections.items():
                if concept_a in statement and concept_b in statement:
                    result["observations_found"] = data["frequency"]
                    result["evidence_check"] = (
                        data["frequency"] == item["supporting_observations"]
                    )
                    matched = result["evidence_check"]

                    result["explanation"] = (
                        f"Both concepts appeared together in "
                        f"{data['frequency']} memories."
                    )
                    break

        if matched:
            result["status"] = "evidence_supported"

        elif not result["explanation"]:
            result["explanation"] = (
                "No matching repeated pattern was found."
            )

        verified_results.append(result)

    return {
        "total_checked": len(verified_results),
        "evidence_supported": sum(
            1 for item in verified_results
            if item["evidence_check"]
        ),
        "results": verified_results,
        "verification_scope": (
            "Checks evidence in stored memories only; "
            "does not establish universal truth."
        )
    }
