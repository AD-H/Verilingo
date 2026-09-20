from verifier import verify_claim


claim = "The RBI will discontinue UPI."

evidence = (
    "The Reserve Bank of India has not announced "
    "that UPI will be discontinued."
)

result = verify_claim(claim, evidence)

print("Claim:")
print(claim)

print("\nEvidence:")
print(evidence)

print("\nVerdict:")
print(result)