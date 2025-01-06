import json
from pprint import pprint

import requests
from sqlalchemy import text

from detroit_tech_employment import db_engine, setup_logging
from detroit_tech_employment.auth import refresh_auth
from detroit_tech_employment.throttle import throttle


@throttle(0.25)
def workflow(code, auth):
    url = "https://emsiservices.com/occupation-benchmark/dimensions/soc"

    body = {
    "id": code,
    "datasets": [
        "commonSkills",
        "definingSkills",
        "distinguishingSkills",
        "typicalEducation",
        "education",
        "riskScore",
        "salary",
        "salaryBoostingSkills",
        "feederOccupations",
        "locationQuotient",
        "experience",
        "employment",
        "employers",
        "demand"
    ],
    "region": {
        "nation": "us",
        "level": "msa",
        "id": "19820"
    }
    }

    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    response = requests.request("POST", url, json=body, headers=headers)

    with open("occupation_benchmarks_msa_19820_20250104.jsonl", "a") as f:
        json.dump(response.json(), f)



if __name__ == "__main__":
    logger = setup_logging()
    auth = refresh_auth()

    # See SOC codes repo to download and integrate this dataset
    top_lev_codes_q = text("""
    SELECT *
    FROM soc.definitions
    WHERE definition IS NOT NULL
    ORDER BY code;
    """)

    with db_engine.connect() as db:
        result = db.execute(top_lev_codes_q)
        rows = result.fetchall()


    for i, row in enumerate(rows):
        workflow(row.code)

        if (i % 50) == 0:
            logger.info(f"{i} occupations downloaded.")
