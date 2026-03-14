"""
Lambda: Postcode lookup from S3 (postcodes.json).
Configure: BUCKET_NAME, OBJECT_KEY (e.g. data/postcodes.json).
API Gateway: GET /api/postcode/{postcode} → Lambda proxy integration.
"""
import json
import os

import boto3

# Set in Lambda environment: S3 bucket and key for postcodes.json
BUCKET_NAME = os.environ.get("BUCKET_NAME", "")
OBJECT_KEY = os.environ.get("OBJECT_KEY", "data/postcodes.json")

# Cache parsed lookup in warm invocations (same container reused)
_lookup_cache = None


def build_lookup(s3_client):
    """Fetch postcodes.json from S3 and build postcode -> first valid row."""
    global _lookup_cache
    if _lookup_cache is not None:
        return _lookup_cache
    if not BUCKET_NAME or not OBJECT_KEY:
        return None
    try:
        resp = s3_client.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY)
        data = json.loads(resp["Body"].read().decode("utf-8"))
    except Exception:
        return None
    lookup = {}
    for p in data:
        if not isinstance(p, dict):
            continue
        pc = p.get("postcode")
        lat = p.get("latitude")
        lng = p.get("longitude")
        if pc is None or lat is None or lng is None:
            continue
        if (float(lat), float(lng)) == (0.0, 0.0):
            continue
        if str(pc) not in lookup:
            lookup[str(pc)] = {
                "postcode": str(pc),
                "suburb": p.get("suburb") or "",
                "state": p.get("state") or "",
                "latitude": float(lat),
                "longitude": float(lng),
            }
    _lookup_cache = lookup
    return lookup


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Content-Type": "application/json",
    }


def handler(event, context):
    """API Gateway proxy integration: event has pathParameters.postcode."""
    headers = cors_headers()
    try:
        path_params = event.get("pathParameters") or {}
        postcode = (path_params.get("postcode") or "").strip()
    except Exception:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"detail": "Invalid request"}),
        }

    if not postcode or not postcode.isdigit():
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"detail": "Postcode must be digits"}),
        }

    s3 = boto3.client("s3")
    lookup = build_lookup(s3)
    if lookup is None:
        return {
            "statusCode": 503,
            "headers": headers,
            "body": json.dumps({"detail": "Postcode data unavailable"}),
        }

    # Try as-is and normalized (no leading zeros)
    postcode_normalized = str(int(postcode))
    for key in (postcode, postcode_normalized):
        if key in lookup:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(lookup[key]),
            }

    return {
        "statusCode": 404,
        "headers": headers,
        "body": json.dumps({"detail": "Postcode not found"}),
    }
