from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

from web_retrieval import retrieve_web_evidence
from demo_verifier import verify_evidence
from s3_storage import save_verification


app = FastAPI(
    title="VeriLingo API",
    description="AI-powered multilingual claim verification system"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClaimRequest(BaseModel):
    claim: str


@app.get("/")
def home():
    return {
        "message": "VeriLingo API is running"
    }


@app.post("/verify")
def verify(data: ClaimRequest):

    # Step 1: Retrieve live web evidence
    evidence_results = retrieve_web_evidence(
        data.claim,
        max_sources=5,
        top_k=5
    )

    # Step 2: Verify the claim
    result = verify_evidence(
        data.claim,
        evidence_results
    )

    # Step 3: Create complete verification result
    verification_result = {
        "claim": data.claim,
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "explanation": result["explanation"],
        "retrieved_evidence": evidence_results
    }

    # Step 4: Store result in Amazon S3
    try:
        s3_key = save_verification(
            verification_result
        )
        storage_status = "Saved to Amazon S3"
    except Exception as error:
        print("S3 upload failed:", error)
        s3_key = None
        storage_status = "S3 upload failed"

    # Step 5: Return result to frontend
    return {
        **verification_result,
        "cloud_storage": storage_status,
        "s3_object_key": s3_key
    }