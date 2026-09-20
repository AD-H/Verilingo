from retrieval import retrieve_evidence


claim = "The RBI will discontinue UPI."

results = retrieve_evidence(claim)

print("\nClaim:")
print(claim)

print("\nRetrieved Evidence:")

for result in results:
    print("\nSource:", result["source"])
    print("Evidence:", result["text"])
    print("Similarity:", result["similarity_score"])