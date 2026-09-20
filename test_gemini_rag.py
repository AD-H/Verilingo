from retrieval import retrieve_evidence
from rag import build_context
from prompt import create_verification_prompt
from gemini_verifier import verify_with_gemini


claim = "The RBI will discontinue UPI."


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


# Step 3: Create verification prompt
prompt = create_verification_prompt(
    context
)


# Step 4: Send prompt to Gemini
result = verify_with_gemini(
    prompt
)


print("\n===== GEMINI VERIFICATION =====")
print(result)