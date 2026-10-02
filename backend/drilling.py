"""Pre-drilling depth screening; deliberately not a success prediction model."""
from pydantic import BaseModel, Field


class DrillingInput(BaseModel):
    planned_depth_ft: float = Field(gt=0, le=1500)
    estimated_water_table_ft: float = Field(gt=0, le=1000)


def assess_drilling(data: DrillingInput):
    margin = round(data.planned_depth_ft - data.estimated_water_table_ft, 2)
    reaches = margin > 0
    summary = (
        f"The planned depth is {margin:g} ft below the estimated water table. "
        "This passes the depth check, but does not establish that drilling will produce usable water."
        if reaches else
        f"The planned depth does not extend below the estimated water table "
        f"(shortfall: {abs(margin):g} ft). Review the depth estimate before drilling."
    )
    return {
        "assessment_type": "drilling",
        "planned_depth_ft": data.planned_depth_ft,
        "estimated_water_table_ft": data.estimated_water_table_ft,
        "depth_margin_ft": margin,
        "depth_check": "passes" if reaches else "review_required",
        "success_probability": None,
        "summary": summary,
        "next_step": "Ask a qualified hydrogeologist to assess the site's water-bearing layers, recharge and expected yield.",
        "limitation": "Drilling success is unconfirmed. No drilling-outcome model is trained; this is a depth comparison only. Groundwater depth alone cannot establish usable yield.",
    }
