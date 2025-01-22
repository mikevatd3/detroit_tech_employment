import pandera as pa
from pandera.typing import Series
import numpy as np
import datetime


class Skills(pa.DataFrameModel):
    """
    COMPLETE
    """
    id: str = pa.Field(nullable=False)
    name: str = pa.Field(nullable=False)
    description: str = pa.Field(nullable=True)
    embedding: Series[np.ndarray] = pa.Field(nullable=False)
    # search vector for ts_search

    class Config:
        strict = True


class Occupation(pa.DataFrameModel):
    """
    COMPLETE
    """
    geoid: str = pa.Field() # All Detroit-Warren-Dearborn for now 
    code: str = pa.Field(nullable=False, unique=True)
    name: str = pa.Field(nullable=False)
    description: str = pa.Field(nullable=True)
    risk_score: float = pa.Field()
    location_quotient: float = pa.Field()
    mean_experience: float = pa.Field()
    mean_salary: float = pa.Field()
    embedding: Series[np.ndarray] = pa.Field(nullable=False)
    start: datetime.date = pa.Field()
    end: datetime.date = pa.Field(default=datetime.date(year=9999, month=12, day=31))
    # search vector for ts_search

    class Config:
        strict = True
        coerce = True
        unique=["msa", "code"]


class HistoricalEarnings(pa.DataFrameModel):
    """
    TODO
    """
    code: str = pa.Field()
    geoid: str = pa.Field()
    year: datetime.date = pa.Field()
    average_hourly: float = pa.Field()
    median_annual: float = pa.Field()


class Positions(pa.DataFrameModel):
    """
    TODO
    """
    code: str = pa.Field()
    geoid: str = pa.Field()
    year: datetime.date = pa.Field()
    jobs: float = pa.Field()
    residence_jobs: float = pa.Field()
    openings: float = pa.Field()
    replacements: float = pa.Field()
    growth: float = pa.Field()


class EarningsDistribution(pa.DataFrameModel):
    """
    TODO
    """
    code: str = pa.Field()
    geoid: str = pa.Field()
    hourly_10th_pctl: float = pa.Field(nullable=True)
    hourly_25th_pctl: float = pa.Field(nullable=True)
    hourly_50th_pctl: float = pa.Field(nullable=True)
    hourly_75th_pctl: float = pa.Field(nullable=True)
    hourly_90th_pctl: float = pa.Field(nullable=True)
    hourly_mean: float = pa.Field()
    median_annual: float = pa.Field()
    start: datetime.date = pa.Field()
    end: datetime.date = pa.Field(default=datetime.date(year=9999, month=12, day=31))

    class Config:
        strict = True
        coerce = True
        unique=["code", "geoid"]


class SkillsSought(pa.DataFrameModel):
    """
    COMPLETE
    """
    occ_code: str = pa.Field(nullable=False)
    skill_id: str = pa.Field(nullable=False)
    significance: str = pa.Field(
        nullable=False, 
        checks=pa.Check.isin(
            {"common", "defining", "distinguishing", "salary-boosting"}
        )
    )
    percentage: float = pa.Field(nullable=False)

    class Config:
        strict = True
        coerce = True
        unique=["skill_id", "occ_code", "relationship"]


class FeederOccupations(pa.DataFrameModel):
    """
    COMPLETE
    Which occupations feed into a current occupations?
    """
    current: str = pa.Field(nullable=False) # Lightcast SOC Code
    next_step: str = pa.Field(nullable=False) # Lightcast SOC Code
    mean_salary_diff: float = pa.Field()
    category: str = pa.Field()
    score: float = pa.Field() # Some kind of likelihood thing?


class ExperienceLevel(pa.DataFrameModel):
    """
    COMPLETE
    A small table containing the description of each experience level.
    """
    id: int
    description: str


class ExperienceRequired(pa.DataFrameModel):
    """
    COMPLETE
    A many-to-many table holding the distribution of the experience 
    required for a given occupation.
    """
    code: str
    exp_level_id: int
    percentage: float


class EducationLevel(pa.DataFrameModel):
    """
    COMPLETE
    Table holding descriptions of each education level.
    """
    id: int
    description: str


class EducationRequired(pa.DataFrameModel):
    """
    COMPLETE
    Many-to-many table holding the distribution of the education required
    for a given occupation.
    """
    code: str
    ed_level_id: int
    count: int
    percentage: float
    typical: bool

