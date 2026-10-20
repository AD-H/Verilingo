from s3_storage import save_verification

test_result = {
    "claim": "India has won a FIFA World Cup",
    "verdict": "CONTRADICTED",
    "confidence": "HIGH",
    "source": "VeriLingo AWS test"
}

key = save_verification(test_result)

print("Uploaded successfully!")
print("S3 object:", key)