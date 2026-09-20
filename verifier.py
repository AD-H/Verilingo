def verify_claim(claim, evidence):

    claim_lower = claim.lower()
    evidence_lower = evidence.lower()

    # Words/phrases that indicate negation
    negative_words = [
        "not",
        "no",
        "never",
        "discontinued",
        "banned",
        "false",
        "denied",
        "cancelled",
        "canceled",
        "does not",
        "will not"
    ]

    # Check whether evidence contains a negative statement
    evidence_is_negative = any(
        word in evidence_lower
        for word in negative_words
    )

    # Check whether claim itself contains a negative statement
    claim_is_negative = any(
        word in claim_lower
        for word in negative_words
    )

    # Simple baseline logic
    if evidence_is_negative and not claim_is_negative:
        verdict = "CONTRADICTED"

    elif not evidence_is_negative and claim_is_negative:
        verdict = "CONTRADICTED"

    else:
        verdict = "SUPPORTED"

    return verdict