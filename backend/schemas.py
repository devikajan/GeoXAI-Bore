from typing import Literal

from pydantic import BaseModel, Field


class BorewellInput(BaseModel):
    Borewell_Depth_ft: float = Field(ge=50, le=1500)
    Water_Table_Depth_ft: float = Field(ge=10, le=1000)
    Pump_Age_years: float = Field(ge=0, le=30)
    Daily_Usage_hours: float = Field(ge=0.5, le=24)

    Soil_Type: Literal["Sandy", "Rocky", "Clayey", "Loamy", "Laterite"]
    Region_Type: Literal["Coastal", "Plateau", "Plains", "Hilly", "Semi-Arid"]

    Annual_Rainfall_mm: float = Field(ge=100, le=4000)
    Maintenance_Frequency_per_year: float = Field(ge=0, le=6)
    Motor_Temperature_C: float = Field(ge=25, le=130)
    Vibration_Level_mms: float = Field(ge=0, le=20)
    Voltage_Fluctuation_pct: float = Field(ge=0, le=40)
    Water_Yield_LPH: float = Field(ge=20, le=5000)
    Casing_Pipe_Age_years: float = Field(ge=0, le=40)
