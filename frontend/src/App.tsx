import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { predictBatch, predictBorewell, requiredInputFields } from './api'
import type { BorewellInput, FeatureExplanation, PredictionResult } from './api'
import './App.css'

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

const soilTypes = ['Sandy', 'Rocky', 'Clayey', 'Loamy', 'Laterite']
const regionTypes = ['Coastal', 'Plateau', 'Plains', 'Hilly', 'Semi-Arid']

type BatchRow = { source: Record<string, string>; prediction: PredictionResult }

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
  const [batchRows, setBatchRows] = useState<BatchRow[]>([])
  const [batchFileName, setBatchFileName] = useState('')
  const [batchError, setBatchError] = useState('')
  const [isBatchLoading, setIsBatchLoading] = useState(false)

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
    setForm(initialForm)
    setResult(null)
    setError('')
  }

  const handleBatchUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setBatchError('')
    setBatchRows([])
    setBatchFileName(file.name)
    setIsBatchLoading(true)
    try {
      const parsed = parseCsv(await file.text())
      const missingFields = requiredInputFields.filter((field) => !parsed.headers.includes(field))
      if (!parsed.records.length) throw new Error('The CSV does not contain any data rows.')
      if (missingFields.length) throw new Error(`Missing required columns: ${missingFields.join(', ')}`)

      const inputs = parsed.records.map((record) => toBorewellInput(record))
      const predictions = await predictBatch(inputs)
      setBatchRows(parsed.records.map((source, index) => ({ source, prediction: predictions[index] })))
    } catch (uploadError) {
      setBatchError(uploadError instanceof Error ? uploadError.message : 'Unable to process this CSV file.')
    } finally {
      setIsBatchLoading(false)
    }
  }

  const probability = result ? result.ensemble_probability * 100 : 0

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="GeoXAI-Bore home">
          <span className="brand-mark">GX</span>
          <span><strong>GeoXAI-Bore</strong><small>Groundwater failure intelligence</small></span>
        </a>
        <nav aria-label="Primary navigation"><a className="active" href="#assessment">Assessment</a><a href="#batch">Batch upload</a></nav>
        <span className="service-pill"><i /> API ready</span>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy"><p className="eyebrow">Single-site assessment / 01</p><h1>Know the risk before the water stops.</h1><p className="hero-text">Combine field conditions, pump telemetry, and maintenance history to surface a six-month failure risk for one borewell.</p><div className="hero-note"><span>13</span> signals evaluated by a Random Forest + XGBoost ensemble</div></div>
        <div className="hero-diagram" aria-label="Borewell monitoring illustration"><div className="rings"><span /><span /><span /></div><div className="well-line"><b>WELL</b><span>2,840 ft monitored depth</span></div><div className="water-line"><span>aquifer layer</span></div></div>
      </section>

      <section className="workspace" id="assessment">
        <form className="assessment-form" onSubmit={submitPrediction}>
          <div className="section-heading"><div><p className="eyebrow">Input profile</p><h2>Describe the borewell</h2></div><span className="required-note">All fields required</span></div>
          <fieldset><legend>Site &amp; hydrology</legend><div className="field-grid">
            <NumberField label="Borewell depth" suffix="ft" value={form.Borewell_Depth_ft} min={50} max={1500} step={10} onChange={(value) => updateField('Borewell_Depth_ft', value)} />
            <NumberField label="Water table depth" suffix="ft" value={form.Water_Table_Depth_ft} min={10} max={1000} step={10} onChange={(value) => updateField('Water_Table_Depth_ft', value)} />
            <NumberField label="Water yield" suffix="LPH" value={form.Water_Yield_LPH} min={20} max={5000} step={50} onChange={(value) => updateField('Water_Yield_LPH', value)} />
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

        <aside className={`result-panel ${result ? 'has-result' : ''}`} aria-live="polite">
          {result ? <><ResultView result={result} probability={probability} /><button className="genai-button" type="button" disabled title="GenAI integration is not available yet">Generate field brief ✦</button></> : <div className="empty-result"><div className="target-icon">◎</div><p className="eyebrow">Awaiting profile</p><h2>Your risk signal will appear here.</h2><p>Complete the profile and run an assessment to see the ensemble probability and the factors shaping it.</p><div className="empty-rule"><span /><small>Model output</small><span /></div></div>}
        </aside>
      </section>

      <section className="batch-section" id="batch"><div className="section-heading"><div><p className="eyebrow">Batch assessment / 02</p><h2>Score a dataset</h2></div><span className="required-note">CSV upload</span></div><p className="batch-intro">Upload a CSV containing the same 13 model features. Extra columns are preserved in memory for this session.</p><label className="upload-zone"><input type="file" accept=".csv,text/csv" onChange={handleBatchUpload} disabled={isBatchLoading} /><span className="upload-icon">↑</span><strong>{isBatchLoading ? 'Scoring dataset...' : 'Choose a CSV dataset'}</strong><small>{batchFileName || 'Required columns are listed in the README'}</small></label>{batchError && <div className="error-banner" role="alert"><strong>Dataset not accepted.</strong> {batchError}</div>}{batchRows.length > 0 && <BatchSummary rows={batchRows} />}</section>

      <section className="method-strip" id="method"><p className="eyebrow">How it works</p><div><strong>01 / Predict</strong><span>Ensemble probability from two tree-based models.</span></div><div><strong>02 / Explain</strong><span>SHAP identifies the strongest risk drivers.</span></div><div><strong>03 / Act</strong><span>Use the signal to prioritize field inspection.</span></div></section>
      <footer><span>GeoXAI-Bore / research demonstrator</span><span>For planning support, not safety-critical decisions</span></footer>
    </main>
  )
}

function NumberField({ label, suffix, value, min, max, step, onChange }: NumberFieldProps) {
  return <label className="field"><span>{label}</span><div className="input-wrap"><input type="number" required min={min} max={max} step={step} value={value} onChange={(event) => onChange(event.target.value)} /><em>{suffix}</em></div></label>
}

function SelectField({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return <label className="field"><span>{label}</span><div className="input-wrap select-wrap"><select value={value} onChange={(event) => onChange(event.target.value)}>{options.map((option) => <option key={option}>{option}</option>)}</select><em>⌄</em></div></label>
}

function ResultView({ result, probability }: { result: PredictionResult; probability: number }) {
  const categoryClass = result.risk_category.toLowerCase()
  return <div className="result-content"><div className="result-topline"><p className="eyebrow">Assessment result</p><span className={`risk-badge ${categoryClass}`}>{result.risk_category} risk</span></div><div className="score-wrap"><div className={`score-ring ${categoryClass}`} style={{ '--score': `${probability * 3.6}deg` } as React.CSSProperties}><div><strong>{probability.toFixed(1)}%</strong><span>6-month failure probability</span></div></div></div><div className="model-split"><div><span>Random Forest</span><strong>{(result.random_forest_probability * 100).toFixed(1)}%</strong></div><div><span>XGBoost</span><strong>{(result.xgboost_probability * 100).toFixed(1)}%</strong></div></div><div className="drivers"><div className="drivers-heading"><h3>What is driving this?</h3><span>SHAP influence</span></div>{result.top_features.map((feature) => <FeatureRow key={feature.feature} feature={feature} />)}</div></div>
}

function FeatureRow({ feature }: { feature: FeatureExplanation }) {
  const positive = feature.shap_value > 0
  return <div className="feature-row"><span className={`feature-dot ${positive ? 'positive' : 'negative'}`}>{positive ? '+' : '-'}</span><div><strong>{feature.feature}</strong><small>{feature.impact}</small></div><b className={positive ? 'positive-text' : 'negative-text'}>{positive ? '+' : ''}{feature.shap_value.toFixed(3)}</b></div>
}

function BatchSummary({ rows }: { rows: BatchRow[] }) {
  const high = rows.filter(({ prediction }) => prediction.risk_category === 'High').length
  const medium = rows.filter(({ prediction }) => prediction.risk_category === 'Medium').length
  const low = rows.length - high - medium
  return <div className="batch-results"><div className="batch-metrics"><div><strong>{rows.length}</strong><small>rows scored</small></div><div><strong className="high-text">{high}</strong><small>high risk</small></div><div><strong className="medium-text">{medium}</strong><small>medium risk</small></div><div><strong className="low-text">{low}</strong><small>low risk</small></div></div><div className="batch-table-wrap"><table><thead><tr><th>Row</th><th>Risk</th><th>Probability</th></tr></thead><tbody>{rows.slice(0, 20).map((row, index) => <tr key={`${index}-${row.prediction.risk_category}`}><td>{index + 1}</td><td><span className={`table-risk ${row.prediction.risk_category.toLowerCase()}`}>{row.prediction.risk_category}</span></td><td>{(row.prediction.ensemble_probability * 100).toFixed(1)}%</td></tr>)}</tbody></table></div><small className="table-note">Showing up to the first 20 scored rows.</small></div>
}

function parseCsv(text: string): { headers: string[]; records: Record<string, string>[] } {
  const rows: string[][] = []
  let row: string[] = []
  let cell = ''
  let quoted = false
  for (let index = 0; index < text.length; index += 1) {
    const character = text[index]
    if (character === '"' && text[index + 1] === '"' && quoted) { cell += '"'; index += 1 }
    else if (character === '"') quoted = !quoted
    else if (character === ',' && !quoted) { row.push(cell.trim()); cell = '' }
    else if ((character === '\n' || character === '\r') && !quoted) { if (character === '\r' && text[index + 1] === '\n') index += 1; row.push(cell.trim()); if (row.some(Boolean)) rows.push(row); row = []; cell = '' }
    else cell += character
  }
  if (cell || row.length) { row.push(cell.trim()); rows.push(row) }
  const headers = (rows.shift() ?? []).map((header) => header.replace(/^\uFEFF/, ''))
  return { headers, records: rows.map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? '']))) }
}

function toBorewellInput(record: Record<string, string>): BorewellInput {
  return Object.fromEntries(requiredInputFields.map((field) => [field, field === 'Soil_Type' || field === 'Region_Type' ? record[field] : Number(record[field])])) as BorewellInput
}

export default App
