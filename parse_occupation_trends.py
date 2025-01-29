import json
import datetime
import pandas as pd


with open("occupation_trends_results_2015_2034_20250122.jsonl") as f:
    append=False

    for i, line in enumerate(f):
        if i > 0:
            append=True

        occ = json.loads(line)

        try:
            # Earnings Distribution
            # Data 1 is the occupation code, and it's the same on all rows
            print(f"Loading {occ['data'][1]['rows'][0]} {i+1}/799", end="")
        except IndexError:
            print(occ)
            continue


        earn_distribution_bins = {
            "Area": "geoid",
            "Occupation": "code",
            "Earnings.Percentile10.2023": "hourly_10th_pctl",
            "Earnings.Percentile25.2023": "hourly_25th_pctl",
            "Earnings.Percentile50.2023": "hourly_50th_pctl",
            "Earnings.Percentile75.2023": "hourly_75th_pctl",
            "Earnings.Percentile90.2023": "hourly_90th_pctl",
            "Earnings.Average.2023": "hourly_mean",
            "Earnings.Median.Annual.2023": "median_annual",
        }

        earnings_distribution = pd.DataFrame({
            earn_distribution_bins[item["name"]]: item["rows"]
            for item in occ["data"]
            if item["name"] in earn_distribution_bins 
        }).assign(
            start=datetime.datetime(year=2023,month=1, day=1),
            end=datetime.datetime(year=9999, month=12, day=31)
        )

        earnings_distribution.to_parquet(
            "earnings_distribution_20250121.parquet.gzip", 
            engine="fastparquet", 
            append=append
        )


        # Historical Earnings - years 2015 to 2023

        years = []
        for year in range(2015, 2024):
            hist_earnings_cols = {
                "Area": "geoid",
                "Occupation": "code",
                f"HistoricalEarnings.Average.{year}": "average_hourly",
                f"HistoricalEarnings.Median.Annual.{year}": "median_annual",
            }

            years.append(pd.DataFrame({
                hist_earnings_cols[item["name"]]: item["rows"]
                for item in occ["data"]
                if item["name"] in hist_earnings_cols 
            }).assign(year=datetime.datetime(year=year, month=1, day=1)))

        pd.concat(years, axis=0).to_parquet(
            "historical_earnings_20250121.parquet.gzip", 
            engine="fastparquet", 
            index=False, 
            append=append
        )

        # Positions

        years = []
        for year in range(2015, 2035):
            positions_cols = {
                f"Area": "geoid",
                f"Occupation": "code",
                f'Jobs.{year}': 'jobs', 
                f'ResidenceJobs.{year}': 'residence_jobs', 
                f'Openings.{year}': 'openings', 
                f'Replacements.{year}': 'replacements', 
                f'Growth.{year}': 'growth',
            }

            years.append(pd.DataFrame({
                positions_cols[item["name"]]: item["rows"]
                for item in occ["data"]
                if item["name"] in positions_cols 
            }).assign(year=datetime.datetime(year=year, month=1, day=1)))

        pd.concat(years, axis=0).to_parquet(
            "positions_20250121.parquet.gzip", 
            engine="fastparquet", 
            index=False, 
            append=append
        )

        print(f": COMPLETE")
