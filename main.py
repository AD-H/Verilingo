import io
import pytesseract
import re
import logging
import os
import boto3
import watchtower
from PIL import Image, ImageOps, ImageFilter, UnidentifiedImageError
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile, File, HTTPException

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

from web_retrieval import retrieve_web_evidence
from demo_verifier import verify_evidence
from s3_storage import save_verification
from dynamodb_storage import save_history, get_history

app = FastAPI(
    title="VeriLingo API",
    description="AI-powered multilingual claim verification system"
)
# ==============================
# AWS CLOUDWATCH LOGGING
# ==============================

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
LOG_GROUP = "verilingo-backend-logs"

cloudwatch_logs = boto3.client(
    "logs",
    region_name=AWS_REGION
)

logger = logging.getLogger("verilingo")
logger.setLevel(logging.INFO)

cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group=LOG_GROUP,
    stream_name="verilingo-local-backend",
    boto3_client=cloudwatch_logs
)

cloudwatch_handler.setLevel(logging.INFO)
logger.addHandler(cloudwatch_handler)

logger.info("VeriLingo CloudWatch logging initialized")
logger.info("VERILINGO CLOUDWATCH TEST SUCCESS")

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
    logger.info("Text verification request received")
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
    logger.info("Text verification completed successfully")
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
        # Step 4: Save searchable report metadata to DynamoDB
    try:
        history_item = save_history(
            verification_result,
            s3_key
        )
        history_status = "Saved to DynamoDB"
    except Exception as error:
        print("DynamoDB upload failed:", error)
        history_item = None
        history_status = "DynamoDB save failed"
    # Step 5: Return result to frontend
    return {
        **verification_result,
        "cloud_storage": storage_status,
        "s3_object_key": s3_key,
        "history_storage": history_status,
        "report_id": (
            history_item["report_id"]
            if history_item else None
        ),
    }
    
@app.get("/history")
def verification_history(limit: int = 20):
    try:
        return {
            "items": get_history(limit),
            "storage": "Amazon DynamoDB"
        }
    except Exception as error:
        print("DynamoDB history retrieval failed:", error)
        return {
            "items": [],
            "storage": "DynamoDB unavailable",
            "error": "Unable to retrieve verification history"
        }
        

@app.post("/verify-image")
async def verify_image(file: UploadFile = File(...)):
    logger.info("Image verification request received")
    # 1. Validate the uploaded file
    allowed_types = {"image/jpeg", "image/png"}

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPG or PNG image."
        )

    # 2. Read and validate the image
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty."
        )

    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image must be smaller than 5 MB."
        )
    logger.info("Image verification completed successfully")
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()

        # Reopen after verify() because verification consumes the stream.
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image."
        )

    # 3. Extract text using local Tesseract OCR
    
    try:
        processed_image = preprocess_image(image)

        raw_text = pytesseract.image_to_string(
            processed_image,
            lang="eng",
            config="--oem 3 --psm 6 -c preserve_interword_spaces=1"
        )

        extracted_text = clean_ocr_text(processed_image)

    except pytesseract.TesseractNotFoundError:
        raise HTTPException(
        status_code=500,
        detail="Tesseract was not found. Check its installation path."
    )


    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail="No readable text found. Try a clearer screenshot."
        )

    if len(extracted_text) > 2000:
        raise HTTPException(
            status_code=422,
            detail=(
                "Too much text was detected. Crop the image "
                "to the claim you want to verify."
            )
        )

    # 4. Retrieve web evidence for the extracted text
    evidence_results = retrieve_web_evidence(
        extracted_text,
        max_sources=5,
        top_k=5
    )

    # 5. Verify using the existing VeriLingo verifier
    result = verify_evidence(
        extracted_text,
        evidence_results
    )

    verification_result = {
        "claim": extracted_text,
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "explanation": result["explanation"],
        "retrieved_evidence": evidence_results,
        "source_type": "image",
        "extracted_text": extracted_text,
        "original_filename": file.filename,
    }

    # 6. Save report to S3
    try:
        s3_key = save_verification(verification_result)
        storage_status = "Saved to Amazon S3"

    except Exception as error:
        print("S3 upload failed:", error)
        s3_key = None
        storage_status = "S3 upload failed"

    # 7. Save history metadata to DynamoDB
    try:
        history_item = save_history(
            verification_result,
            s3_key
        )
        history_status = "Saved to DynamoDB"

    except Exception as error:
        print("DynamoDB upload failed:", error)
        history_item = None
        history_status = "DynamoDB save failed"

    # 8. Return the result to React
    return {
        **verification_result,
        "cloud_storage": storage_status,
        "s3_object_key": s3_key,
        "history_storage": history_status,
        "report_id": (
            history_item["report_id"]
            if history_item else None
        ),
    }

def preprocess_image(image: Image.Image) -> Image.Image:
    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Enlarge small text for better recognition
    image = image.resize(
        (image.width * 2, image.height * 2),
        Image.Resampling.LANCZOS
    )

    # Improve contrast
    image = ImageOps.autocontrast(image)

    # Reduce small specks and noise
    image = image.filter(ImageFilter.MedianFilter(size=3))

    # Convert to black text on a white background
    image = image.point(
        lambda pixel: 255 if pixel > 165 else 0
    )

    return image




def clean_ocr_text(image: Image.Image) -> str:
    data = pytesseract.image_to_data(
        image,
        lang="eng",
        config="--oem 3 --psm 6",
        output_type=pytesseract.Output.DICT
    )

    lines = {}

    for i, word in enumerate(data["text"]):
        word = word.strip()

        if not word:
            continue

        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            continue

        # Ignore low-confidence OCR words
        if confidence < 45:
            continue

        key = (
            data["block_num"][i],
            data["par_num"][i],
            data["line_num"][i]
        )

        lines.setdefault(key, []).append(word)

    return "\n".join(
        " ".join(words)
        for words in lines.values()
    )
