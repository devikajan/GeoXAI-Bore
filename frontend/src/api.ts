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

const API_URL = import.meta.env.PROD
  ? '/api'
  : (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000')

export async function checkApiHealth(): Promise<boolean> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 65000)
  try {
    const response = await fetch(`${API_URL}/health`, { signal: controller.signal })
    return response.ok
  } catch {
    return false
  } finally {
    window.clearTimeout(timeout)
  }
}

export type ChatMessage = { role: 'user' | 'assistant'; content: string }
export type AssistantLanguage = 'auto' | 'en' | 'te' | 'hi' | 'ta' | 'kn' | 'ml' | 'mr' | 'bn' | 'gu' | 'pa' | 'ur' | 'or'
export type DrillingInput = { planned_depth_ft: number; estimated_water_table_ft: number }
export type DrillingResult = DrillingInput & {
  assessment_type: 'drilling'
  depth_margin_ft: number
  depth_check: 'passes' | 'review_required'
  success_probability: null
  summary: string
  next_step: string
  limitation: string
}
export type AssistantAssessment = Pick<PredictionResult, 'risk_category' | 'ensemble_probability' | 'top_features'> | DrillingResult

export async function assessDrilling(input: DrillingInput): Promise<DrillingResult> {
  const response = await fetch(`${API_URL}/drilling/assess`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input),
    signal: AbortSignal.timeout(65000),
  })
  if (!response.ok) throw new Error('The drilling depth check could not be completed. Please review the inputs and try again.')
  return response.json()
}

export async function sendChat(messages: ChatMessage[], language: AssistantLanguage, assessment?: AssistantAssessment): Promise<string> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 65000)
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: messages.slice(-19).map((message) => ({ ...message, content: message.content.slice(0, 4000) })),
        language,
        simple_mode: true,
        assessment,
      }),
      signal: controller.signal,
    })
    const data = await response.json()
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'The assistant could not process this message.')
    return data.reply
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw new Error('The assistant took too long. Please try again.')
    if (error instanceof TypeError) throw new Error('Cannot reach the assistant. Start the backend on port 8000.')
    throw error
  } finally { window.clearTimeout(timeout) }
}

export async function predictBorewell(input: BorewellInput): Promise<PredictionResult> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })
  } catch {
    throw new Error(`Cannot reach the prediction API at ${API_URL}. Start the backend and try again.`)
  }

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Prediction failed with status ${response.status}`)
  }

  return response.json() as Promise<PredictionResult>
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
