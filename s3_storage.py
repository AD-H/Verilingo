import boto3
import json
from datetime import datetime, timezone

BUCKET_NAME = "verilingo-results-658548982345-ap-south-1-an"

s3 = boto3.client(
    "s3",
    region_name="ap-south-1"
)


def save_verification(result):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    key = f"verifications/{timestamp}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        ContentType="application/json"
    )

    return key