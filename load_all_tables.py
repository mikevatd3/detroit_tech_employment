import datetime
import click
import tomli
import pandas as pd
from sqlalchemy.orm import sessionmaker

from metadata_audit.capture import record_metadata
import detroit_tech_employment.schema as s
from detroit_tech_employment import setup_logging, metadata_engine, db_engine


logger = setup_logging()

with open("metadata.toml", "rb") as md:
    metadata = tomli.load(md)


def occupation_cleanup(df):
    return (
        df.rename(columns={"msa": "geoid"})
        .drop(["typical_education", "embedding"], axis=1)
        .assign(end=datetime.date(year=9999, month=12, day=31)) # Forever
    )


def earnings_distribution_cleanup(df):
    return df.assign(end=datetime.date(year=9999, month=12, day=31))

def skills_cleanup(df):
    return df.drop("embedding", axis=1)

def skills_sought_cleanup(df):
    return df.rename(columns={"soc": "occ_code"})


tablename_and_schema = (
    # ("skills", s.Skills, skills_cleanup),
    # ("occupation", s.Occupation, occupation_cleanup),
    # ("historical_earnings", s.HistoricalEarnings, lambda x: x),
    # ("positions", s.Positions, lambda x: x),
    ("earnings_distribution", s.EarningsDistribution, earnings_distribution_cleanup),
    ("skills_sought", s.SkillsSought, skills_sought_cleanup),
    ("feeder_occupations", s.FeederOccupations, lambda x: x),
    ("experience_level", s.ExperienceLevel, lambda x: x),
    ("experience_required", s.ExperienceRequired, lambda x: x),
    ("education_level", s.EducationLevel, lambda x: x),
    ("education_required", s.EducationRequired, lambda x: x),
)


@click.command()
@click.argument("edition_date")
def main(edition_date):
    """
    This opens every table related to a single edition date (see 
    metadata) and loads them into the db whether they are a csv or parquet.

    Includes metadata push as well.
    """

    for tablename, Schema, cleanup_func in tablename_and_schema:
        edition = metadata["tables"][tablename]["editions"][edition_date]

        logger.info(f"Loading {tablename}.")

        filepath = edition["raw_path"]

        if filepath.endswith(".parquet.gzip"):
            rows = cleanup_func(pd.read_parquet(filepath))

        elif filepath.endswith(".csv"):
            rows = cleanup_func(pd.read_csv(filepath))
        else:
            raise NotImplementedError("This file cannot be loaded automatically")
        
        logger.info(f"{tablename} loaded successfully. Validating.")

        validated = Schema.validate(rows)

        with metadata_engine.connect() as db:
            logger.info("Connected to metadata schema.")

            record_metadata(
                Schema,
                __file__,
                tablename,
                metadata,
                edition_date,
                validated,
                sessionmaker(bind=db)(),
                logger,
            )

            db.commit()
            logger.info("successfully recorded metadata")

    with db_engine.connect() as db:
        logger.info("Metadata recorded, pushing data to db.")

        validated.to_sql(  # type: ignore
            tablename, db, index=False, schema="detroit_tech_employment", if_exists="replace"
        )


if __name__ == "__main__":
    main()