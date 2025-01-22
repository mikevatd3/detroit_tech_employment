import json
from itertools import islice

import requests
import pandas as pd
from sqlalchemy import text

from detroit_tech_employment import db_engine
from detroit_tech_employment.auth import refresh_auth
from detroit_tech_employment.reference import REGIONAL_ZIPS
from detroit_tech_employment.throttle import throttle


auth = refresh_auth()
headers = {
    "Authorization": f"Bearer {auth['access_token']}",
    "Content-Type": "application/json"
}


@throttle(0.5)
def staffing_pull(codes: list[str]):
    url = "https://agnitio.emsicloud.com/emsi.us.staffing/2024.2"

    payload = {
        "metrics": [
            {"name": "Jobs.2001"},
            {"name": "Jobs.2002"},
            {"name": "Jobs.2003"},
            {"name": "Jobs.2004"},
            {"name": "Jobs.2005"},
            {"name": "Jobs.2006"},
            {"name": "Jobs.2007"},
            {"name": "Jobs.2008"},
            {"name": "Jobs.2009"},
            {"name": "Jobs.2010"},
            {"name": "Jobs.2011"},
            {"name": "Jobs.2012"},
            {"name": "Jobs.2013"},
            {"name": "Jobs.2014"},
            {"name": "Jobs.2015"},
            {"name": "Jobs.2016"},
            {"name": "Jobs.2017"},
            {"name": "Jobs.2018"},
            {"name": "Jobs.2019"},
            {"name": "Jobs.2020"},
            {"name": "Jobs.2021"},
            {"name": "Jobs.2022"},
            {"name": "Jobs.2023"},
            {"name": "Jobs.2024"},
            {"name": "Jobs.2025"},
            {"name": "Jobs.2026"},
            {"name": "Jobs.2027"},
            {"name": "Jobs.2028"},
            {"name": "Jobs.2029"},
            {"name": "Jobs.2030"},
            {"name": "Jobs.2031"},
            {"name": "Jobs.2032"},
            {"name": "Jobs.2033"},
            {"name": "Jobs.2034"}
        ],

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
                "map": {
                    code.code: [code.code]
                    for code in codes
                },
            },
        ]
    }

    response = requests.request("post", url, headers=headers, json=payload)

    return response.json()


def chunked(iterable, chunksize):
    iterator = iter(iterable)
    while chunk := list(islice(iterator, chunksize)):
        yield chunk


# Gather all occupations

q = text("""
select *
from soc.lightcast_definitions;
""")


with db_engine.connect() as db:
    result = db.execute(q)
    rows = result.fetchall()


results = []
for i, codes in enumerate(chunked(rows, 10)):
    print(f"Starting pull {i+1}/80:", end=" ")
    results.append(staffing_pull(codes))

    with open("staffing_results_2001_2034.json", "a") as f:
        f.write(json.dumps(results) + '\n')

    print("COMPLETE")
