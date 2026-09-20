from retrieval import retrieve_evidence
from rag import build_context

claim = "The RBI will discontinue UPI."

evidence_results = retrieve_evidence(
    claim,
    top_k=3
)

context = build_context(
    claim,
    evidence_results
)

print(context)