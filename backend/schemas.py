from pydantic import BaseModel
class BorewellInput(BaseModel):

    Borewell_Depth_ft: float
    Water_Table_Depth_ft: float
    Pump_Age_years: float
    Daily_Usage_hours: float

    Soil_Type: str
    Region_Type: str

    Annual_Rainfall_mm: float
    Maintenance_Frequency_per_year: float
    Motor_Temperature_C: float
    Vibration_Level_mms: float
    Voltage_Fluctuation_pct: float
    Water_Yield_LPH: float
    Casing_Pipe_Age_years: float