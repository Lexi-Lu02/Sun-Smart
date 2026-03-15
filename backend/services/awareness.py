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


# globle preloading
AGE_DATA = read_s3(AGE_FILE)
STATE_DATA = read_s3(STATE_FILE)
MORTALITY_DATA = read_s3(MORTALITY_FILE)
SUN_DATA = read_s3(SUN_FILE)


def get_incidence_age():
    data = AGE_DATA
    result = defaultdict(int)

    for row in data:
        if row["Year"] != "2023":
            continue
        if row["Sex"] != "Persons":
            continue

        age = row["Age group"]
        count = int(row["Count"])
        result[age] += count

    return result


def get_incidence_state():
    data = STATE_DATA
    result = defaultdict(int)

    for row in data:
        if row["Year"] != "2023":
            continue
        if row["Sex"] != "Persons":
            continue

        state = row["State or territory"]
        count = int(row["Count"])
        result[state] += count

    return result


def get_mortality():
    data = MORTALITY_DATA
    result = defaultdict(int)

    for row in data:
        if row["Year"] != "2023":
            continue
        if row["Sex"] != "Persons":
            continue

        cancer = row["Cancer type"]
        count = int(row["Count"])
        result[cancer] += count

    return result


def get_sun_data():
    return SUN_DATA


def lambda_handler(event, context):
    path = event.get("rawPath", "")

    if path == "/incidence-age":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(get_incidence_age())
        }

    elif path == "/incidence-state":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(get_incidence_state())
        }

    elif path == "/mortality":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(get_mortality())
        }

    elif path == "/sun":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(get_sun_data())
        }

    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not found"})
    }