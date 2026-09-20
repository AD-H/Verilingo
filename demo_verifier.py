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

    negative_words = {
        "no",
        "not",
        "never",
        "none",
        "neither",
        "without",
        "denied",
        "denies",
        "deny",
        "false",
        "falsely",
        "incorrect",
        "inaccurate",
        "debunked",
        "disproved",
        "refuted",
        "cancelled",
        "canceled"
    }

    words = set(text.split())

    return len(words.intersection(negative_words)) > 0

def has_uncertainty(text):
    text = normalize(text)

    uncertainty_words = {
        "could",
        "might",
        "may",
        "possibly",
        "possible",
        "perhaps",
        "hypothesis",
        "theory",
        "theoretical",
        "unproven",
        "uncertain",
        "unclear",
        "speculated",
        "speculation",
        "proposed",
        "suggests",
        "suggest",
        "potential",
        "potentially"
    }

    words = set(text.split())

    return len(
        words.intersection(uncertainty_words)
    ) > 0

def split_sentences(text):
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 10
    ]


def analyze_sentence(claim, sentence, similarity_score):

    claim_words = get_words(claim)
    sentence_words = get_words(sentence)

    if not claim_words or not sentence_words:
        return 0, 0

    overlap = (
        len(claim_words.intersection(sentence_words))
        / len(claim_words)
    )

    relevance = (
        0.65 * similarity_score +
        0.35 * overlap
    )

    if relevance < 0.30:
        return 0, 0

    claim_negative = has_negation(claim)
    sentence_negative = has_negation(sentence)

    # Explicit opposite polarity
    if claim_negative != sentence_negative:
        return 0, relevance

    # Evidence is conditional, hypothetical,
    # speculative, or explicitly unproven.
    # It should not be treated as direct support.
    if has_uncertainty(sentence):
        return 0, 0

    return relevance, 0


def analyze_evidence(claim, evidence):
    sentences = split_sentences(
        evidence["text"]
    )

    if not sentences:
        sentences = [evidence["text"]]

    similarity = evidence.get(
        "similarity_score",
        0
    )

    best_support = 0
    best_contradiction = 0

    for sentence in sentences:

        support, contradiction = analyze_sentence(
            claim,
            sentence,
            similarity
        )

        best_support = max(
            best_support,
            support
        )

        best_contradiction = max(
            best_contradiction,
            contradiction
        )

    return best_support, best_contradiction


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
                "The retrieved evidence is relevant to "
                "the claim, but does not clearly establish "
                "whether it is true or false."
            )
        }

    support_ratio = total_support / total
    contradiction_ratio = (
        total_contradiction / total
    )

    if (
        contradiction_ratio >= 0.60
        and contradicting_sources >= 1
    ):

        confidence = "HIGH"

        if contradiction_ratio < 0.80:
            confidence = "MEDIUM"

        return {
            "verdict": "CONTRADICTED",
            "confidence": confidence,
            "explanation": (
                "The retrieved web evidence contains "
                "explicit statements that conflict with "
                "the claim."
            )
        }

    if (
        support_ratio >= 0.60
        and supporting_sources >= 1
    ):

        confidence = "HIGH"

        if support_ratio < 0.80:
            confidence = "MEDIUM"

        return {
            "verdict": "SUPPORTED",
            "confidence": confidence,
            "explanation": (
                "The retrieved web evidence contains "
                "statements consistent with the claim."
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