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

let healthRequest: Promise<boolean> | null = null
let lastHealthyAt = 0

export function checkApiHealth(): Promise<boolean> {
  if (healthRequest) return healthRequest
  healthRequest = probeApiHealth().finally(() => { healthRequest = null })
  return healthRequest
}

async function probeApiHealth(): Promise<boolean> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 12000)
  try {
    const response = await fetch(`${API_URL}/health`, { signal: controller.signal, cache: 'no-store' })
    const data: unknown = response.ok ? await response.json() : null
    const healthy = Boolean(data && typeof data === 'object' && 'status' in data && data.status === 'healthy')
    if (healthy) lastHealthyAt = Date.now()
    else lastHealthyAt = 0
    return healthy
  } catch {
    lastHealthyAt = 0
    return false
  } finally {
    window.clearTimeout(timeout)
  }
}

async function waitForApi() {
  if (Date.now() - lastHealthyAt < 20000) return
  const deadline = Date.now() + 90000
  do {
    if (await checkApiHealth()) return
    await new Promise(resolve => window.setTimeout(resolve, 3000))
  } while (Date.now() < deadline)
  throw new Error('The server has not finished starting. Use Reconnect at the top of the page and try again when it says API ready.')
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

export type ReferenceSite = {
  id: string; station: string; district: string; mandal: string; geology: string
  water_level_m: number; discharge_lps: number; source: string; measurement_date: string | null
}
export type SiteResult = {
  assessment_type: 'drilling_site'; site: ReferenceSite; desired_yield_lph: number
  reference_yield_lph: number; reference_water_depth_ft: number
  evidence_status: 'reference_meets_target' | 'reference_below_target'
  success_probability: null; summary: string; next_step: string; limitation: string
}

export async function getDrillingSites(): Promise<ReferenceSite[]> {
  await waitForApi()
  const response = await fetch(`${API_URL}/drilling/sites`, { signal: AbortSignal.timeout(20000) })
  if (!response.ok) throw new Error('Location data is unavailable. Please reconnect and retry.')
  return response.json()
}

export async function assessSite(siteId: string, desiredYield: number): Promise<SiteResult> {
  await waitForApi()
  const response = await fetch(`${API_URL}/drilling/site-assess`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ site_id: siteId, desired_yield_lph: desiredYield }), signal: AbortSignal.timeout(20000),
  })
  if (!response.ok) throw new Error('The location assessment is unavailable. Choose a listed station and try again.')
  return response.json()
}

export async function assessDrilling(input: DrillingInput): Promise<DrillingResult> {
  await waitForApi()
  const response = await fetch(`${API_URL}/drilling/assess`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input),
    signal: AbortSignal.timeout(65000),
  })
  if (!response.ok) throw new Error('The drilling depth check could not be completed. Please review the inputs and try again.')
  return response.json()
}

export async function sendChat(messages: ChatMessage[], language: AssistantLanguage, assessment?: AssistantAssessment | SiteResult): Promise<string> {
  await waitForApi()
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
    if (error instanceof TypeError) throw new Error('Cannot reach the assistant. Use Reconnect and try again when the API is ready.')
    throw error
  } finally { window.clearTimeout(timeout) }
}

export async function predictBorewell(input: BorewellInput): Promise<PredictionResult> {
  await waitForApi()
  let response: Response
  try {
    response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
      signal: AbortSignal.timeout(65000),
    })
  } catch {
    throw new Error('The prediction service did not respond. Reconnect and try again when the API is ready.')
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
