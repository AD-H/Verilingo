import re


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_words(text):
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were",
        "be", "been", "being", "has", "have", "had",
        "will", "would", "shall", "should",
        "to", "of", "in", "on", "at", "for", "from",
        "and", "or", "but", "that", "this", "it",
        "with", "by", "as", "about", "into", "during",
        "there", "their", "they", "them"
    }

    return {
        word
        for word in normalize(text).split()
        if len(word) > 2 and word not in stop_words
    }


def has_negation(text):
    text = normalize(text)

    patterns = [
        r"\bno\b",
        r"\bnot\b",
        r"\bnever\b",
        r"\bnone\b",
        r"\bneither\b",
        r"\bwithout\b",
        r"\bdenied\b",
        r"\bdenies\b",
        r"\bdeny\b",
        r"\bfalse\b",
        r"\bfalsely\b",
        r"\bincorrect\b",
        r"\binaccurate\b",
        r"\bdebunked\b",
        r"\bdisproved\b",
        r"\brefuted\b",
        r"\bwon't\b",
        r"\bwouldn't\b",
        r"\bcan't\b",
        r"\bcannot\b",
        r"\bdoesn't\b",
        r"\bdon't\b",
        r"\ndidn't\b",
        r"\bisn't\b",
        r"\baren't\b",
        r"\bwasn't\b",
        r"\bweren't\b",
        r"\bhasn't\b",
        r"\bhaven't\b",
        r"\bhadn't\b"
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def analyze_evidence(claim, evidence):
    claim_words = get_words(claim)
    evidence_words = get_words(evidence["text"])

    if not claim_words:
        return 0, 0

    overlap = len(
        claim_words.intersection(evidence_words)
    ) / len(claim_words)

    similarity = evidence.get(
        "similarity_score",
        0
    )

    relevance = (
        0.65 * similarity +
        0.35 * overlap
    )

    claim_negative = has_negation(claim)
    evidence_negative = has_negation(
        evidence["text"]
    )

    support = 0
    contradiction = 0

    if relevance < 0.30:
        return support, contradiction

    if claim_negative == evidence_negative:
        support = relevance
    else:
        contradiction = relevance

    return support, contradiction


def verify_evidence(claim, evidence_results):

    if not evidence_results:
        return {
            "verdict": "UNCERTAIN",
            "confidence": "LOW",
            "explanation": (
                "No relevant evidence was found "
                "from the live web."
            )
        }

    total_support = 0
    total_contradiction = 0

    supporting_sources = 0
    contradicting_sources = 0

    for evidence in evidence_results:

        support, contradiction = analyze_evidence(
            claim,
            evidence
        )

        total_support += support
        total_contradiction += contradiction

        if support > contradiction and support > 0:
            supporting_sources += 1

        elif contradiction > support and contradiction > 0:
            contradicting_sources += 1

    total = (
        total_support +
        total_contradiction
    )

    if total == 0:
        return {
            "verdict": "UNCERTAIN",
            "confidence": "LOW",
            "explanation": (
                "The retrieved sources are related to "
                "the claim but do not provide enough "
                "evidence to determine its truth."
            )
        }

    support_ratio = total_support / total
    contradiction_ratio = (
        total_contradiction / total
    )

    # Clear supporting evidence
    if (
        support_ratio >= 0.65
        and supporting_sources >= 1
    ):
        if support_ratio >= 0.80 and supporting_sources >= 2:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"

        return {
            "verdict": "SUPPORTED",
            "confidence": confidence,
            "explanation": (
                f"The retrieved web evidence contains "
                f"{supporting_sources} source(s) that are "
                f"consistent with the claim."
            )
        }

    # Clear contradictory evidence
    if (
        contradiction_ratio >= 0.65
        and contradicting_sources >= 1
    ):
        if (
            contradiction_ratio >= 0.80
            and contradicting_sources >= 2
        ):
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"

        return {
            "verdict": "CONTRADICTED",
            "confidence": confidence,
            "explanation": (
                f"The retrieved web evidence contains "
                f"{contradicting_sources} source(s) that "
                f"conflict with the claim."
            )
        }

    return {
        "verdict": "UNCERTAIN",
        "confidence": "LOW",
        "explanation": (
            "The retrieved sources provide mixed or "
            "insufficient evidence to establish whether "
            "the claim is true or false."
        )
    }