from pathlib import Path
import json
import logging
import logging.config
import pandas as pd
from sqlalchemy import create_engine
import tomli


with open(Path().cwd() / "config.toml", "rb") as f:
    config = tomli.load(f)


db_engine = create_engine(
    f"postgresql+psycopg2://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
    connect_args={'options': f'-csearch_path={config["app"]["name"]},public'},
)

metadata_engine = create_engine(
    f"postgresql+psycopg2://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
    connect_args={'options': f'-csearch_path={config["db"]["metadata_schema"]},public'},
)


def setup_logging():
    with open(Path.cwd() / "logging_config.json") as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)

    return logging.getLogger(config["app"]["name"])


def convert_to_df(response):
    fields =  response["data"]
    return pd.DataFrame({field["name"]: field["rows"] for field in fields})