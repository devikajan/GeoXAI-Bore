import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { assessDrilling, sendChat } from './api'
import type { AssistantLanguage, DrillingResult } from './api'
import { resultLanguages } from './resultLanguages'

export default function DrillingAssessment({ result, onResult }: {
  result: DrillingResult | null
  onResult: (result: DrillingResult | null) => void
}) {
  const [depth, setDepth] = useState(450)
  const [waterTable, setWaterTable] = useState(280)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const active = useRef(true)
  useEffect(() => {
    active.current = true
    return () => { active.current = false }
  }, [])

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    onResult(null)
    try {
      const response = await assessDrilling({ planned_depth_ft: depth, estimated_water_table_ft: waterTable })
      if (active.current) onResult(response)
    }
    catch { if (active.current) setError('The depth check is unavailable. Please try again when the API is ready.') }
    finally { if (active.current) setBusy(false) }
  }

  return <section className="workspace">
    <form className="assessment-form" onSubmit={submit} data-spotlight="light">
      <span className="surface-glow" aria-hidden="true" />
      <div className="section-heading"><div><p className="eyebrow">01 / New drilling</p><h2>Check a proposed borewell</h2></div></div>
      <p className="assessment-description">Start with a preliminary depth check. Use the estimated groundwater depth from a local survey.</p>
      <fieldset disabled={busy}><legend>Before drilling</legend><div className="field-grid drilling-fields">
        <label className="field"><span>Planned drilling depth</span><div className="input-wrap"><input type="number" required min="1" max="1500" step="any" value={depth} onChange={event => { setDepth(Number(event.target.value)); onResult(null) }} /><em>ft</em></div></label>
        <label className="field"><span>Estimated water table depth</span><div className="input-wrap"><input type="number" required min="1" max="1000" step="any" value={waterTable} onChange={event => { setWaterTable(Number(event.target.value)); onResult(null) }} /><em>ft</em></div></label>
      </div></fieldset>
      <div className="drilling-notice"><strong>Drilling success prediction needs outcome data.</strong><p>The available model was trained for maintenance failure. This option compares depths only; it cannot predict whether the new borewell will produce usable water.</p></div>
      <div className="form-actions"><button className="primary-button" disabled={busy} type="submit">{busy ? 'Checking…' : 'Check planned depth'} <span>→</span></button><button className="quiet-button" type="button" disabled={busy} onClick={() => { setDepth(0); setWaterTable(0); onResult(null); setError('') }}>Reset fields</button></div>
      {error && <p className="error-banner" role="alert">{error}</p>}
    </form>
    <aside className="result-panel" aria-live="polite" data-spotlight="light"><span className="surface-glow" aria-hidden="true" />
      {result ? <DrillingResultView result={result} /> : <div className="empty-result"><span className="result-kicker">Preliminary site check</span><div className="target-icon">◎</div><h2>Review the planned drilling depth.</h2><p>See how the planned depth compares with the estimated water table. A site survey is needed to establish water-bearing layers and expected yield.</p></div>}
    </aside>
  </section>
}

function DrillingResultView({ result }: { result: DrillingResult }) {
  const [language, setLanguage] = useState<AssistantLanguage>('en')
  const [translated, setTranslated] = useState<{ key: string; text: string; error: boolean } | null>(null)
  const [retry, setRetry] = useState(0)
  const key = `${JSON.stringify(result)}:${language}:${retry}`
  const local = `${result.summary} ${result.next_step} ${result.limitation}`
  const settled = translated?.key === key
  useEffect(() => {
    if (language === 'en') return
    let active = true
    void sendChat([{ role: 'user', content: 'Explain this drilling depth check in simple words in the selected language. State that success is unconfirmed and no probability is available. Do not interpret it as a six-month maintenance prediction.' }], language, result)
      .then(text => { if (active) setTranslated({ key, text, error: false }) })
      .catch(() => { if (active) setTranslated({ key, text: '', error: true }) })
    return () => { active = false }
  }, [key, language, result])
  const maxDepth = Math.max(result.planned_depth_ft, result.estimated_water_table_ft)
  return <div className="result-content">
    <p className="eyebrow">Drilling depth assessment</p>
    <h2>{result.depth_check === 'passes' ? 'Depth check passes' : 'Planned depth needs review'}</h2>
    <p className="drilling-outcome">Drilling success: <strong>Unconfirmed</strong></p>
    <div className="depth-chart" role="img" aria-label={`Planned depth ${result.planned_depth_ft} feet; estimated water table ${result.estimated_water_table_ft} feet. Depth margin ${result.depth_margin_ft} feet.`}>
      <h3>Depth comparison</h3>
      <p>Feet below ground · longer bars mean greater depth</p>
      <div><span>Planned drilling</span><b>{result.planned_depth_ft} ft</b><i style={{ width: `${result.planned_depth_ft / maxDepth * 100}%` }} /></div>
      <div><span>Estimated water table</span><b>{result.estimated_water_table_ft} ft</b><i className="water-depth" style={{ width: `${result.estimated_water_table_ft / maxDepth * 100}%` }} /></div>
      <p><strong>{Math.abs(result.depth_margin_ft)} ft</strong> {result.depth_margin_ft > 0 ? 'below the estimated water table' : result.depth_margin_ft < 0 ? 'short of the estimated water table' : 'margin — planned depth equals the estimated water table'}</p>
    </div>
    <section className="result-explanation"><div className="explanation-heading"><h4>What this means</h4><label>Language<select value={language} onChange={event => setLanguage(event.target.value as AssistantLanguage)}>{resultLanguages.map(option => <option key={option.code} value={option.code}>{option.label}</option>)}</select></label></div>
      <p className="explanation-copy">{language === 'en' ? local : settled && translated.text ? translated.text : local}</p>
      {language !== 'en' && !settled && <p role="status">Preparing translation…</p>}
      {language !== 'en' && settled && translated.error && <div className="explanation-error" role="alert">Translation unavailable. Showing English.<button type="button" onClick={() => setRetry(value => value + 1)}>Retry</button></div>}
    </section>
  </div>
}
