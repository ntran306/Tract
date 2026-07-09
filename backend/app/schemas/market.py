from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class HPIPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: date
    index_value: Decimal


class HPISeries(BaseModel):
    state: str
    region_name: str
    latest_period: date
    latest_index: Decimal
    points: list[HPIPoint]


class FMRRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    area_code: str
    area_name: str
    state: str
    bedrooms: int
    rent: Decimal


class RentBenchmark(BaseModel):
    """Actual rent vs area FMR, phrased neutrally (above FMR isn't 'bad')."""

    rent: Decimal
    fmr: Decimal
    area_name: str
    bedrooms: int
    delta_pct: Decimal  # (rent - fmr) / fmr * 100, one decimal
