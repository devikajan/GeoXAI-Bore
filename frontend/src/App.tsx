import { useEffect, useRef, useState } from 'react'
import type { FormEvent, PointerEvent as ReactPointerEvent } from 'react'
import { checkApiHealth, predictBorewell } from './api'
import type { BorewellInput, PredictionResult } from './api'
import './App.css'
import AssistantChat from './AssistantChat'
import ResultGraphs from './ResultGraphs'
import ResultExplanation from './ResultExplanation'

const initialForm: BorewellInput = {
  Borewell_Depth_ft: 450,
  Water_Table_Depth_ft: 280,
  Pump_Age_years: 4,
  Daily_Usage_hours: 7,
  Soil_Type: 'Sandy',
  Region_Type: 'Plains',
  Annual_Rainfall_mm: 900,
  Maintenance_Frequency_per_year: 1,
  Motor_Temperature_C: 58,
  Vibration_Level_mms: 2.2,
  Voltage_Fluctuation_pct: 8,
  Water_Yield_LPH: 1200,
  Casing_Pipe_Age_years: 6,
}

const emptyForm: BorewellInput = {
  Borewell_Depth_ft: 0,
  Water_Table_Depth_ft: 0,
  Pump_Age_years: 0,
  Daily_Usage_hours: 0,
  Soil_Type: '',
  Region_Type: '',
  Annual_Rainfall_mm: 0,
  Maintenance_Frequency_per_year: 0,
  Motor_Temperature_C: 0,
  Vibration_Level_mms: 0,
  Voltage_Fluctuation_pct: 0,
  Water_Yield_LPH: 0,
  Casing_Pipe_Age_years: 0,
}

const soilTypes = ['Sandy', 'Rocky', 'Clayey', 'Loamy', 'Laterite']
const regionTypes = ['Coastal', 'Plateau', 'Plains', 'Hilly', 'Semi-Arid']

type NumberFieldProps = {
  label: string
  suffix: string
  value: number
  min: number
  max: number
  step: number
  onChange: (value: string) => void
}

function App() {
  const [form, setForm] = useState<BorewellInput>(initialForm)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [apiStatus, setApiStatus] = useState<'checking' | 'ready' | 'offline'>('checking')
  const activeSpotlight = useRef<HTMLElement | null>(null)

  useEffect(() => {
    let active = true
    async function updateApiStatus() {
      const available = await checkApiHealth()
      if (active) setApiStatus(available ? 'ready' : 'offline')
    }
    void updateApiStatus()
    const timer = window.setInterval(updateApiStatus, 30000)
    window.addEventListener('focus', updateApiStatus)
    return () => {
      active = false
      window.clearInterval(timer)
      window.removeEventListener('focus', updateApiStatus)
    }
  }, [])

  function updateSurfaceSpotlight(event: ReactPointerEvent<HTMLElement>) {
    const surface = (event.target as Element).closest<HTMLElement>('[data-spotlight]')
    if (activeSpotlight.current && activeSpotlight.current !== surface) {
      activeSpotlight.current.style.setProperty('--spot-active', '0')
    }
    activeSpotlight.current = surface
    if (!surface) return
    const bounds = surface.getBoundingClientRect()
    surface.style.setProperty('--spot-x', `${event.clientX - bounds.left}px`)
    surface.style.setProperty('--spot-y', `${event.clientY - bounds.top}px`)
    surface.style.setProperty('--spot-active', '1')
  }

  function hideSurfaceSpotlight() {
    activeSpotlight.current?.style.setProperty('--spot-active', '0')
    activeSpotlight.current = null
  }

  const updateField = (field: keyof BorewellInput, value: string) => {
    setForm((current) => ({
      ...current,
      [field]: typeof current[field] === 'number' ? Number(value) : value,
    }))
  }

  const submitPrediction = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      setResult(await predictBorewell(form))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to reach the prediction service.')
    } finally {
      setIsLoading(false)
    }
  }

  const resetForm = () => {
    setForm(emptyForm)
    setResult(null)
    setError('')
  }

  return (
    <main className="app-shell" onPointerMove={updateSurfaceSpotlight} onPointerLeave={hideSurfaceSpotlight}>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="GeoXAI-Bore home">
          <span className="brand-mark">GX</span>
          <span><strong>GeoXAI-Bore</strong><small>Groundwater failure intelligence</small></span>
        </a>
        <nav aria-label="Primary navigation"><a className="active" href="#assessment">Assessment</a><a href="#method">Method</a></nav>
        <span className={`service-pill ${apiStatus}`} role="status"><i /> {apiStatus === 'ready' ? 'API ready' : apiStatus === 'offline' ? 'API offline' : 'Connecting'}</span>
      </header>

      <section className="hero" id="top" data-spotlight="dark">
        <span className="surface-glow" aria-hidden="true" />
        <div className="hero-copy"><p className="eyebrow">Explainable groundwater intelligence</p><h1>Know the risk before the water stops.</h1><p className="hero-text">Combine field conditions, pump telemetry, and maintenance history to surface an explainable six-month failure risk for one borewell.</p><div className="hero-actions"><a className="hero-primary" href="#assessment">Run an assessment <span>→</span></a><a className="hero-secondary" href="#method">Explore the method</a></div><div className="hero-note"><span>13</span> signals evaluated by a Random Forest + XGBoost ensemble</div></div>
        <div className="hero-diagram" aria-label="Borewell monitoring illustration"><div className="diagram-status"><span>Live model</span><strong>RF + XGB</strong></div><div className="rings"><span /><span /><span /></div><div className="well-line"><b>WELL</b><span>single-site risk profile</span></div><div className="water-line"><span>aquifer layer</span></div></div>
      </section>

      <section className="proof-strip" aria-label="Model highlights" data-spotlight="light"><span className="surface-glow" aria-hidden="true" /><div><strong>13</strong><span>Field and equipment signals</span></div><div><strong>02</strong><span>Models in the ensemble</span></div><div><strong>05</strong><span>Top SHAP factors explained</span></div><div><strong>06 mo</strong><span>Prediction horizon</span></div></section>

      <section className="workspace" id="assessment">
        <form className="assessment-form" onSubmit={submitPrediction} data-spotlight="light">
          <span className="surface-glow" aria-hidden="true" />
          <div className="section-heading"><div><p className="eyebrow">Input profile</p><h2>Describe the borewell</h2></div><span className="required-note">All fields required</span></div>
          <fieldset><legend>Site &amp; hydrology</legend><div className="field-grid">
            <NumberField label="Borewell depth" suffix="ft" value={form.Borewell_Depth_ft} min={50} max={1500} step={10} onChange={(value) => updateField('Borewell_Depth_ft', value)} />
            <NumberField label="Water table depth" suffix="ft" value={form.Water_Table_Depth_ft} min={10} max={1000} step={10} onChange={(value) => updateField('Water_Table_Depth_ft', value)} />
            <NumberField label="Water yield" suffix="LPH" value={form.Water_Yield_LPH} min={20} max={5000} step={10} onChange={(value) => updateField('Water_Yield_LPH', value)} />
            <SelectField label="Soil type" value={form.Soil_Type} options={soilTypes} onChange={(value) => updateField('Soil_Type', value)} />
            <SelectField label="Region type" value={form.Region_Type} options={regionTypes} onChange={(value) => updateField('Region_Type', value)} />
            <NumberField label="Annual rainfall" suffix="mm" value={form.Annual_Rainfall_mm} min={100} max={4000} step={50} onChange={(value) => updateField('Annual_Rainfall_mm', value)} />
          </div></fieldset>
          <fieldset><legend>Equipment &amp; usage</legend><div className="field-grid">
            <NumberField label="Pump age" suffix="years" value={form.Pump_Age_years} min={0} max={30} step={0.5} onChange={(value) => updateField('Pump_Age_years', value)} />
            <NumberField label="Casing pipe age" suffix="years" value={form.Casing_Pipe_Age_years} min={0} max={40} step={0.5} onChange={(value) => updateField('Casing_Pipe_Age_years', value)} />
            <NumberField label="Daily usage" suffix="hours" value={form.Daily_Usage_hours} min={0.5} max={24} step={0.5} onChange={(value) => updateField('Daily_Usage_hours', value)} />
            <NumberField label="Motor temperature" suffix="°C" value={form.Motor_Temperature_C} min={25} max={130} step={1} onChange={(value) => updateField('Motor_Temperature_C', value)} />
            <NumberField label="Vibration level" suffix="mm/s" value={form.Vibration_Level_mms} min={0} max={20} step={0.1} onChange={(value) => updateField('Vibration_Level_mms', value)} />
            <NumberField label="Voltage fluctuation" suffix="%" value={form.Voltage_Fluctuation_pct} min={0} max={40} step={0.5} onChange={(value) => updateField('Voltage_Fluctuation_pct', value)} />
            <NumberField label="Maintenance visits" suffix="per year" value={form.Maintenance_Frequency_per_year} min={0} max={6} step={1} onChange={(value) => updateField('Maintenance_Frequency_per_year', value)} />
          </div></fieldset>
          <div className="form-actions"><button className="primary-button" type="submit" disabled={isLoading}>{isLoading ? 'Assessing...' : 'Run assessment'} <span>→</span></button><button className="quiet-button" type="button" onClick={resetForm}>Reset fields</button></div>
          {error && <div className="error-banner" role="alert"><strong>Prediction unavailable.</strong> {error}<small>Start the API with <code>uvicorn backend.main:app --reload</code>.</small></div>}
        </form>

        <aside className={`result-panel ${result ? 'has-result' : ''}`} aria-live="polite" data-spotlight="light">
          <span className="surface-glow" aria-hidden="true" />
          {result ? <ResultView result={result} /> : <div className="empty-result"><span className="result-kicker">Live model output</span><div className="target-icon">◎</div><p className="eyebrow">Awaiting profile</p><h2>Your risk signal will appear here.</h2><p>Complete the profile and run an assessment to see the ensemble probability and the factors shaping it.</p><div className="empty-rule"><span /><small>Explainable prediction</small><span /></div></div>}
        </aside>
      </section>

      <section className="method-strip" id="method"><p className="eyebrow">How it works</p><div data-spotlight="light"><span className="surface-glow" aria-hidden="true" /><strong>01 / Predict</strong><span>Ensemble probability from two tree-based models.</span></div><div data-spotlight="light"><span className="surface-glow" aria-hidden="true" /><strong>02 / Explain</strong><span>SHAP identifies the strongest risk drivers.</span></div><div data-spotlight="light"><span className="surface-glow" aria-hidden="true" /><strong>03 / Act</strong><span>Use the signal to prioritize field inspection.</span></div></section>
      <footer><span>GeoXAI-Bore / research demonstrator</span><span>For planning support, not safety-critical decisions</span></footer>
      <AssistantChat result={result} />
    </main>
  )
}

function NumberField({ label, suffix, value, min, max, step, onChange }: NumberFieldProps) {
  return <label className="field"><span>{label}</span><div className="input-wrap"><input type="number" required min={min} max={max} step={step} value={value} onChange={(event) => onChange(event.target.value)} /><em>{suffix}</em></div></label>
}

function SelectField({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return <label className="field"><span>{label}</span><div className="input-wrap select-wrap"><select required value={value} onChange={(event) => onChange(event.target.value)}><option value="" disabled>Select</option>{options.map((option) => <option key={option}>{option}</option>)}</select><em>⌄</em></div></label>
}

function ResultView({ result }: { result: PredictionResult }) {
  const categoryClass = result.risk_category.toLowerCase()
  return <div className="result-content"><div className="result-topline"><p className="eyebrow">Assessment result</p><span className={`risk-badge ${categoryClass}`}>{result.risk_category} risk</span></div><ResultGraphs result={result} /><ResultExplanation result={result} /></div>
}

export default App
