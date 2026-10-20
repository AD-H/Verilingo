import os
import boto3
from datetime import datetime, timezone
from uuid import uuid4

REGION = "ap-south-1"
TABLE_NAME = "VeriLingoHistory"

dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION
)

table = dynamodb.Table(TABLE_NAME)


def save_history(result, s3_key=None):
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()

    report_id = str(uuid4())

    item = {
        "pk": "VERIFICATION",
        "sk": f"{timestamp}#{report_id}",
        "report_id": report_id,
        "created_at": timestamp,
        "claim": result.get("claim", ""),
        "verdict": result.get("verdict", "UNCERTAIN"),
        "confidence": result.get("confidence", "LOW"),
        "evidence_count": len(
            result.get("retrieved_evidence", [])
        ),
        "s3_object_key": s3_key or ""
    }

    table.put_item(Item=item)

    return item


def get_history(limit=20):
    response = table.query(
        KeyConditionExpression=(
            boto3.dynamodb.conditions.Key("pk").eq(
                "VERIFICATION"
            )
        ),
        ScanIndexForward=False,
        Limit=max(1, min(limit, 100))
    )

    return response.get("Items", [])