"""Location-based reference evidence, without fabricating drilling-success labels."""
import json
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field


class ReferenceSite(BaseModel):
    id: str
    station: str
    district: str
    mandal: str
    geology: str
    water_level_m: float = Field(ge=0)
    discharge_lps: float = Field(ge=0)
    source: str
    measurement_date: str | None


class SiteInput(BaseModel):
    site_id: str = Field(min_length=1, max_length=100)
    desired_yield_lph: float = Field(gt=0, le=100000)


class SiteResult(BaseModel):
    assessment_type: Literal['drilling_site'] = 'drilling_site'
    site: ReferenceSite
    desired_yield_lph: float
    reference_yield_lph: float
    reference_water_depth_ft: float
    evidence_status: Literal['reference_meets_target', 'reference_below_target']
    success_probability: None = None
    summary: str
    next_step: str
    limitation: str


@lru_cache(maxsize=1)
def reference_sites():
    path = Path(__file__).resolve().parents[1] / 'data' / 'drilling_reference_sites.json'
    return [ReferenceSite.model_validate(row) for row in json.loads(path.read_text(encoding='utf-8'))]


def assess_site(data: SiteInput):
    site = next((site for site in reference_sites() if site.id == data.site_id), None)
    if site is None:
        raise LookupError('This location has no reference record. Choose a listed station.')
    yield_lph = round(site.discharge_lps * 3600, 1)
    meets = yield_lph >= data.desired_yield_lph
    comparison = 'meets' if meets else 'is below'
    return SiteResult(
        site=site, desired_yield_lph=data.desired_yield_lph,
        reference_yield_lph=yield_lph,
        reference_water_depth_ft=round(site.water_level_m * 3.280839895, 1),
        evidence_status='reference_meets_target' if meets else 'reference_below_target',
        summary=f'The {site.station} reference station in {site.mandal}, {site.district} '
                f'records {site.geology} geology and {yield_lph:g} LPH discharge. '
                f'This {comparison} your requested {data.desired_yield_lph:g} LPH. '
                'It describes that station, not the outcome of drilling at your plot.',
        next_step='Use a local hydrogeological survey to check water-bearing fractures, seasonal recharge and expected usable yield at the proposed plot.',
        limitation='Drilling success remains unconfirmed. This is one reference station, not a plot-level prediction. '
                   'The source does not provide a measurement date or labelled drilling outcomes; '
                   'its readings may not represent current conditions. No success probability is available.',
    )
