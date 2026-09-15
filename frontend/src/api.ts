export type BorewellInput = {
  Borewell_Depth_ft: number
  Water_Table_Depth_ft: number
  Pump_Age_years: number
  Daily_Usage_hours: number
  Soil_Type: string
  Region_Type: string
  Annual_Rainfall_mm: number
  Maintenance_Frequency_per_year: number
  Motor_Temperature_C: number
  Vibration_Level_mms: number
  Voltage_Fluctuation_pct: number
  Water_Yield_LPH: number
  Casing_Pipe_Age_years: number
}

export type FeatureExplanation = {
  feature: string
  shap_value: number
  impact: string
}

export type PredictionResult = {
  random_forest_probability: number
  xgboost_probability: number
  ensemble_probability: number
  risk_category: 'Low' | 'Medium' | 'High'
  top_features: FeatureExplanation[]
}

export const requiredInputFields: (keyof BorewellInput)[] = [
  'Borewell_Depth_ft',
  'Water_Table_Depth_ft',
  'Pump_Age_years',
  'Daily_Usage_hours',
  'Soil_Type',
  'Region_Type',
  'Annual_Rainfall_mm',
  'Maintenance_Frequency_per_year',
  'Motor_Temperature_C',
  'Vibration_Level_mms',
  'Voltage_Fluctuation_pct',
  'Water_Yield_LPH',
  'Casing_Pipe_Age_years',
]

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function predictBorewell(input: BorewellInput): Promise<PredictionResult> {
  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Prediction failed with status ${response.status}`)
  }

  return response.json() as Promise<PredictionResult>
}

export async function predictBatch(
  rows: BorewellInput[],
  onProgress?: (completed: number, total: number) => void,
): Promise<PredictionResult[]> {
  const predictions: PredictionResult[] = []

  for (const [index, row] of rows.entries()) {
    predictions.push(await predictBorewell(row))
    onProgress?.(index + 1, rows.length)
  }

  return predictions
}

export type GenAIExplanation = {
  brief: string
  risk_category: 'Low' | 'Medium' | 'High'
  ensemble_probability: number
}

export async function generateExplanation(input: BorewellInput): Promise<GenAIExplanation> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 50000)
  let response: Response
  try {
    response = await fetch(`${API_URL}/genai/explanation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
      signal: controller.signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('Gemini took too long to respond. Check the backend logs and Gemini API configuration.')
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
  }

  if (!response.ok) {
    let detail = `Explanation failed with status ${response.status}`
    try { detail = (await response.json()).detail ?? detail } catch { /* Keep the status fallback. */ }
    throw new Error(detail)
  }

  return response.json() as Promise<GenAIExplanation>
}