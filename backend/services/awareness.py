import json
import boto3
from collections import defaultdict

s3 = boto3.client("s3")

BUCKET = "tp06-bucket1"

AGE_FILE = "2023-Cancer-incidence-by-age-groups.json"
STATE_FILE = "2023-Cancer-incidence-by-state-and-territory.json"
MORTALITY_FILE = "2023-Cancer-mortality.json"
SUN_FILE = "cleaned_sunprotection.json"


def read_s3(key):
    print(f"Reading {key} from S3...")
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    data = obj["Body"].read()
    print(f"{key} size: {len(data)} bytes")
    return json.loads(data)


# global preloading
AGE_DATA = read_s3(AGE_FILE)
STATE_DATA = read_s3(STATE_FILE)
MORTALITY_DATA = read_s3(MORTALITY_FILE)
SUN_DATA = read_s3(SUN_FILE)


def make_response(data, status_code=200):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(data)
    }


def get_incidence_age():
    result = defaultdict(int)

    for row in AGE_DATA:
        if row.get("Year") != "2023":
            continue
        if row.get("Sex") != "Persons":
            continue

        age = row.get("Age group", "Unknown")
        count = row.get("Count", 0)

        try:
            result[age] += int(count)
        except:
            continue

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer incidence by age group"
    }


def get_incidence_state():
    result = defaultdict(int)

    for row in STATE_DATA:
        if row.get("Year") != "2023":
            continue
        if row.get("Sex") != "Persons":
            continue

        state = row.get("State or territory", "Unknown")
        count = row.get("Count", 0)

        try:
            result[state] += int(count)
        except:
            continue

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer incidence by state and territory"
    }


def get_mortality():
    result = defaultdict(int)

    for row in MORTALITY_DATA:
        if row.get("Year") != "2023":
            continue
        if row.get("Sex") != "Persons":
            continue

        cancer = row.get("Cancer type", "Unknown")
        count = row.get("Count", 0)

        try:
            result[cancer] += int(count)
        except:
            continue

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer mortality"
    }


def get_sun_data():
    tips = []
    takeaway = "Stay sun safe with sunscreen, shade, hats, and protective clothing."

    if isinstance(SUN_DATA, list):
        for row in SUN_DATA[:5]:
            if isinstance(row, dict):
                text = row.get("Tip") or row.get("tip") or row.get("Message") or row.get("message")
                if text:
                    tips.append(text)

    if not tips:
        tips = [
            "Use SPF 30+ sunscreen.",
            "Wear protective clothing.",
            "Seek shade during peak UV hours.",
            "Use sunglasses and a hat."
        ]

    return {
        "tips": tips,
        "takeaway": takeaway
    }


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    request_context = event.get("requestContext", {})
    http_method = request_context.get("http", {}).get("method", "")

    # CORS preflight
    if http_method == "OPTIONS":
        return make_response({"message": "CORS OK"})

    query_params = event.get("queryStringParameters") or {}
    data_type = query_params.get("type", "")

    if data_type == "age":
        return make_response(get_incidence_age())

    elif data_type == "state":
        return make_response(get_incidence_state())

    elif data_type == "mortality":
        return make_response(get_mortality())

    elif data_type == "sun":
        return make_response(get_sun_data())

    return make_response({
        "error": "Invalid type",
        "supported_types": ["age", "state", "mortality", "sun"]
    }, 400)