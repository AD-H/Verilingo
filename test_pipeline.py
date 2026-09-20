from retrieval import retrieve_evidence
from rag import build_context
from prompt import create_verification_prompt


claim = "UPI allows users to transfer money between bank accounts."


# Step 1: Retrieve evidence
evidence_results = retrieve_evidence(
    claim,
    top_k=3
)


# Step 2: Build RAG context
context = build_context(
    claim,
    evidence_results
)


# Step 3: Create AI verification prompt
prompt = create_verification_prompt(
    context
)


print("\n========== COMPLETE PIPELINE TEST ==========\n")

print(prompt)

print("\n========== PIPELINE TEST SUCCESS ==========\n")