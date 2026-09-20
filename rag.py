def build_context(claim, evidence_results):

    context = f"Claim:\n{claim}\n\n"
    context += "Relevant Evidence:\n\n"

    for i, evidence in enumerate(evidence_results, start=1):

        context += f"Evidence {i}:\n"
        context += f"Source: {evidence['source']}\n"
        context += f"Text: {evidence['text']}\n"
        context += f"Similarity: {evidence['similarity_score']}\n\n"

    return context