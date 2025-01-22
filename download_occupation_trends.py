import json

import requests
from sqlalchemy import text

from detroit_tech_employment import db_engine
from detroit_tech_employment.auth import refresh_auth
from detroit_tech_employment.reference import REGIONAL_ZIPS
from detroit_tech_employment.throttle import throttle


metrics = []
years = range(2015, 2035)

for year in years:

    if year <= 2023:
        metrics.extend([
            {"name": f"HistoricalEarnings.Average.{year}"},
            {"name": f"HistoricalEarnings.Median.Annual.{year}"},
            {"name": f"ResidenceJobs.{year}"}, # Where workers live!
        ])

    metrics.extend([
        {"name": f"Jobs.{year}"},
        {"name": f"Openings.{year}"}, # Replacements + Growth
        {"name": f"Replacements.{year}"}, # Of workers that will need to be replaced due to leaving the occupation
        {"name": f"Growth.{year}"}, # Gain or loss in positions in occupation
    ])

metrics.extend([
    {
        "name": "Earnings.Average"
    },
    {
        "name": "Earnings.Percentile10"
    },
    {
        "name": "Earnings.Percentile25"
    },
    {
        "name": "Earnings.Percentile50"
    },
    {
        "name": "Earnings.Percentile75"
    },
    {
        "name": "Earnings.Percentile90"
    },
    {
        "name": "Earnings.Median.Annual"
    },
])


# Not required now, but this needs to be refreshed mid-pull
@throttle(0.5)
def staffing_pull(code):
    url = "https://agnitio.emsicloud.com/emsi.us.occupation/2024.2"

    payload = {
        "metrics": metrics,

        "constraints": [
            {
                "dimensionName": "Area",
                "map": {
                    "04000US26": ["26"], # Michigan
                    "05000US26163": ["26163"], # Wayne County
                    "05000US26125": ["26125"], # Oakland County
                    "05000US26099": ["26099"], # Macomb
                    "05000US26161": ["26161"], # Washtenaw
                    "31000US19820": ["MSA19820"], # Detroit-Warren-Dearborn MSA
                    **REGIONAL_ZIPS,
                }
            },
            { 
                "dimensionName": "Occupation", 
                "map": {code.code: [code.code]},
            },
        ]
    }

    response = requests.request("post", url, headers=headers, json=payload)

    return response.json()


# Gather all occupations

q = text("""
select *
from soc.lightcast_definitions;
""")


with db_engine.connect() as db:
    result = db.execute(q)
    rows = result.fetchall()


filename = "occupation_trends_results_2015_2034_20250122.jsonl"


for i, codes in enumerate(rows):

    try:
        print(f"Starting pull {i+1}/799:", end=" ")

        with open(filename, "a") as f:
            f.write(json.dumps(staffing_pull(codes)) + '\n')

        print("COMPLETE")

    except Exception as e:
        print("ERROR")

        auth = refresh_auth()
        headers = {
            "Authorization": f"Bearer {auth['access_token']}",
            "Content-Type": "application/json"
        }

        print(f"Retrying pull {i+1}/799:", end=" ")

        with open(filename, "a") as f:
            f.write(json.dumps(staffing_pull(codes)) + '\n')

        print("COMPLETE")

