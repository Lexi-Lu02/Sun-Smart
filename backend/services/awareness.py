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


# preload data once per container
AGE_DATA = read_s3(AGE_FILE)
STATE_DATA = read_s3(STATE_FILE)
MORTALITY_DATA = read_s3(MORTALITY_FILE)
SUN_DATA = read_s3(SUN_FILE)

# debug logs
print("AGE sample:", AGE_DATA[0] if AGE_DATA else "empty")
print("AGE keys:", list(AGE_DATA[0].keys()) if AGE_DATA and isinstance(AGE_DATA[0], dict) else "no keys")

print("STATE sample:", STATE_DATA[0] if STATE_DATA else "empty")
print("STATE keys:", list(STATE_DATA[0].keys()) if STATE_DATA and isinstance(STATE_DATA[0], dict) else "no keys")

print("MORTALITY sample:", MORTALITY_DATA[0] if MORTALITY_DATA else "empty")
print("MORTALITY keys:", list(MORTALITY_DATA[0].keys()) if MORTALITY_DATA and isinstance(MORTALITY_DATA[0], dict) else "no keys")

print("SUN sample:", SUN_DATA[0] if SUN_DATA else "empty")
print("SUN keys:", list(SUN_DATA[0].keys()) if SUN_DATA and isinstance(SUN_DATA[0], dict) else "no keys")


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


def safe_int(value):
    try:
        return int(float(value))
    except Exception:
        return 0


def get_incidence_age():
    result = defaultdict(int)

    for row in AGE_DATA:
        # keep 2023
        if str(row.get("Year", "")).strip() != "2023":
            continue

        age = str(row.get("Age group (years)", "Unknown")).strip()
        count = safe_int(row.get("Count", 0))

        if not age:
            age = "Unknown"

        result[age] += count

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer incidence by age group"
    }


def get_incidence_state():
    latest_year = -1
    filtered_rows = []

    # find the latest year
    for row in STATE_DATA:
        try:
            y = int(str(row.get("Year", "")).strip())
            if y > latest_year:
                latest_year = y
        except Exception:
            continue

    # Get the latest data for the corresponding year
    for row in STATE_DATA:
        try:
            y = int(str(row.get("Year", "")).strip())
        except Exception:
            continue

        if y != latest_year:
            continue

        filtered_rows.append(row)

    result = defaultdict(int)

    for row in filtered_rows:
        state = str(row.get("State or Territory", "Unknown")).strip()
        count = safe_int(row.get("Count", 0))

        if not state:
            state = "Unknown"

        result[state] += count

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": f"Cancer incidence by state and territory ({latest_year})"
    }


def get_mortality():
    result = defaultdict(int)

    for row in MORTALITY_DATA:
        if str(row.get("Year", "")).strip() != "2023":
            continue

        age_group = str(row.get("Age group (years)", "Unknown")).strip()
        count = safe_int(row.get("Count", 0))

        if not age_group:
            age_group = "Unknown"

        result[age_group] += count

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer mortality by age group"
    }


def get_sun_data():
    tips = []
    takeaway = "Stay sun safe with sunscreen, shade, hats, and protective clothing."

    # table, section, group_label, characteristic, gender, metric, value
    if isinstance(SUN_DATA, list):
        for row in SUN_DATA[:8]:
            if not isinstance(row, dict):
                continue

            characteristic = str(row.get("characteristic", "")).strip()
            metric = str(row.get("metric", "")).strip()
            value = row.get("value", "")

            if characteristic and metric:
                tips.append(f"{characteristic}: {metric} ({value})")

    if not tips:
        tips = [
            "Use SPF 30+ sunscreen.",
            "Wear protective clothing.",
            "Seek shade during peak UV hours.",
            "Use sunglasses and a hat."
        ]

    return {
        "tips": tips[:4],
        "takeaway": takeaway
    }


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    request_context = event.get("requestContext", {})
    http_method = request_context.get("http", {}).get("method", "")

    # CORS
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