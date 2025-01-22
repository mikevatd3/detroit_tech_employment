import json
import pandas as pd
import spacy


nlp = spacy.load("en_core_web_lg")

with open("occupation_benchmarks_msa_19820_20250115.jsonl") as f:
    objs = [json.loads(line) for line in f.readlines()]


occupations = []
feeder_occupations = []
skills = []
soc_skill_joins = []
education_levels = set()
education_level_required = []
experience_levels = set()
experience_required = []


experience_level_names = {
    '0 to 2 years': 1,
    '3 to 5 years': 2, 
    '6 to 8 years': 3, 
    '9+ years': 4, 
}

experience_level_df = pd.DataFrame([
    {"id": v, "description": k} for k, v in experience_level_names.items()
])

experience_level_df.to_csv("experience_levels_20250121.csv")


education_levels = {
    "High school or GED": 0,
    "Associate's degree": 1,
    "Bachelor's degree": 2, 
    "Master's degree": 3,
    "Ph.D. or professional degree": 4,
}

education_level_df = pd.DataFrame([
    {"id": v, "description": k} for k, v in education_levels.items()
])

education_level_df.to_csv("education_levels_20250121.csv")


for obj in objs:
    if "data" not in obj:
        print(obj)
        continue

    # Flatten occupation fields
    occupations.append({
        "msa": "32000US26" + obj["data"]["region"]["id"],
        "code": obj["data"]["id"],
        "name": obj["data"]["name"],
        "description": obj["data"]["description"],
        "risk_score": obj["data"]["riskScore"],
        "location_quotient": obj["data"]["locationQuotient"],
        "typical_education": (
            obj["data"]["typicalEducation"]["id"]
            if (
                ("typicalEducation" in obj["data"])
                and (obj["data"]["typicalEducation"] is not None)
            )
            else None
        ),
        "mean_experience": obj["data"].get("experience", {"mean": None})["mean"],
        "mean_salary": obj["data"].get("salary", {"mean": None})["mean"],
        "embedding": nlp(obj["data"]["description"]).vector,
        "start": "2024-01-01",
        "end": "9999-12-31",
        # search vector for ts_search
    })

    feeder_occupations.extend(
        {
            "current": feeder["id"],
            "next_step": obj["data"]["id"],
            "mean_salary_diff": feeder["meanSalaryDiff"],
            "category": feeder["category"],
            "score": feeder["score"],
        } for feeder in obj["data"]["feederOccupations"]
    )

    soc_code = obj["data"]["id"]
    for skill_type in [
        "commonSkills", 
        "definingSkills", 
        "distinguishingSkills", 
        "salaryBoostingSkills"
    ]:
        skills.extend([
            {
                "id": skill["id"],
                "name": skill["name"],
                "description": skill["description"],
                "embedding": nlp(skill["description"]).vector
            }
            for skill in obj["data"].get(skill_type, [])
        ])
        soc_skill_joins.extend([
            {
                "soc": soc_code,
                "skill_id": skill["id"],
                "count": skill["count"],
                "percentage": skill["percentage"]
            }
            for skill in obj["data"].get(skill_type, [])
        ])
    typical = obj["data"]["typicalEducation"]

    for level in obj["data"]["education"]:
        education_level_required.append({
            "code": obj["data"]["id"],
            "ed_level_id": level["id"],
            "count": level["count"],
            "percentage": level["percentage"],
            "typical": True if level["id"] == typical["id"] else False,
        })
    for level in obj["data"]["experience"]["distribution"]:
        experience_required.append({
            "code": obj["data"]["id"],
            "exp_level_id": experience_level_names[level["key"]],
            "percentage": level["value"],
        })


occupations_df = pd.DataFrame(occupations)
feeder_occupations_df = pd.DataFrame(feeder_occupations)
skills_df = pd.DataFrame(skills).drop_duplicates(subset="id")
join_df = pd.DataFrame(soc_skill_joins)

skills_df.to_parquet("all_skills_20250116.parquet.gzip", index=False)
feeder_occupations_df.to_csv("feeder_occupations_20240121.csv", index=False)
occupations_df.to_parquet("all_occupations_20240120.parquet.gzip", index=False)
join_df.to_csv("skills_required_20250116.csv", index=False)

pd.DataFrame(education_level_required).to_csv("education_level_required_20250121.csv", index=False)
pd.DataFrame(experience_required).to_csv("experience_required_20250121.csv", index=False)