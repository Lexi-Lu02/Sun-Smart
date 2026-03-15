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
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return json.loads(obj["Body"].read())

# AGE INCIDENCE

def get_incidence_age():

    data = read_s3(AGE_FILE)

    result = defaultdict(int)

    for row in data:

        if row["Year"] != "2023":
            continue

        if row["Sex"] != "Persons":
            continue

        age = row["Age group (years)"]
        count = int(row["Count"] or 0)

        result[age] += count

    labels = list(result.keys())
    values = list(result.values())

    return {
        "labels": labels,
        "values": values,
        "datasetLabel": "Cancer Incidence by Age Group (2023)"
    }


# STATE INCIDENCE

def get_incidence_state():

    data = read_s3(STATE_FILE)

    result = defaultdict(int)

    for row in data:

        if row["Year"] != "2023":
            continue

        if row["Sex"] != "Persons":
            continue

        state = row["State or Territory"]
        count = int(row["Count"] or 0)

        result[state] += count

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer Incidence by State (2023)"
    }


# MORTALITY

def get_mortality():

    data = read_s3(MORTALITY_FILE)

    result = defaultdict(int)

    for row in data:

        if row["Year"] != "2023":
            continue

        if row["Sex"] != "Persons":
            continue

        age = row["Age group (years)"]
        count = int(row["Count"] or 0)

        result[age] += count

    return {
        "labels": list(result.keys()),
        "values": list(result.values()),
        "datasetLabel": "Cancer Mortality by Age (2023)"
    }



# SUN PROTECTION

def get_sunprotection():

    data = read_s3(SUN_FILE)

    labels = []
    values = []

    for row in data[:10]:

        labels.append(row["metric"])
        values.append(row["value"])

    return {
        "labels": labels,
        "values": values,
        "datasetLabel": "Sun Protection Behaviour"
    }