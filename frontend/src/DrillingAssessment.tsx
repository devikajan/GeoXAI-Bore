import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { assessSite, getDrillingSites, sendChat } from './api'
import type { AssistantLanguage, ReferenceSite, SiteResult } from './api'
import { resultLanguages } from './resultLanguages'

export default function DrillingAssessment({ result, onResult }: {
  result: SiteResult | null
  onResult: (result: SiteResult | null) => void
}) {
  const [sites, setSites] = useState<ReferenceSite[]>([])
  const [district, setDistrict] = useState(result?.site.district ?? '')
  const [siteId, setSiteId] = useState(result?.site.id ?? '')
  const [target, setTarget] = useState(result?.desired_yield_lph ?? 1000)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [catalogueError, setCatalogueError] = useState('')
  const [retry, setRetry] = useState(0)
  const active = useRef(true)
  useEffect(() => {
    active.current = true
    return () => { active.current = false }
  }, [])
  useEffect(() => {
    let current = true
    void getDrillingSites().then(rows => {
      if (current) { setSites(rows); setCatalogueError('') }
    }).catch(() => { if (current) setCatalogueError('Location data could not be loaded. Reconnect and retry.') })
    return () => { current = false }
  }, [retry])

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    onResult(null)
    try {
      const response = await assessSite(siteId, target)
      if (active.current) onResult(response)
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : 'Location assessment unavailable. Please reconnect and retry.')
    } finally { if (active.current) setBusy(false) }
  }
  const districts = [...new Set(sites.map(site => site.district))].sort()
  const selectedSite = sites.find(site => site.id === siteId)
  return <section className="workspace">
    <form className="assessment-form" onSubmit={submit} data-spotlight="light">
      <span className="surface-glow" aria-hidden="true" />
      <div className="section-heading"><div><p className="eyebrow">01 / New drilling</p><h2>Explore a drilling location</h2></div></div>
      <p className="assessment-description">Select a reference location in Andhra Pradesh to view its recorded groundwater conditions.</p>
      {sites.length === 0 && !catalogueError && <p role="status">Loading locations… the server may take a minute to start.</p>}
      {catalogueError && <div className="explanation-error" role="alert">{catalogueError}<button type="button" onClick={() => setRetry(value => value + 1)}>Retry locations</button></div>}
      <fieldset disabled={busy || sites.length === 0}><legend>Location &amp; water requirement</legend><div className="field-grid drilling-fields">
        <label className="field"><span>District</span><div className="input-wrap"><select required value={district} onChange={event => { setDistrict(event.target.value); setSiteId(''); onResult(null) }}><option value="" disabled>Select a district</option>{districts.map(value => <option key={value}>{value}</option>)}</select></div></label>
        <label className="field"><span>Mandal / reference station</span><div className="input-wrap"><select required value={siteId} onChange={event => { setSiteId(event.target.value); onResult(null) }}><option value="" disabled>Select a reference</option>{sites.filter(site => site.district === district).map(site => <option key={site.id} value={site.id}>{site.mandal} · {site.station}</option>)}</select></div></label>
        <label className="field"><span>Water needed per hour</span><div className="input-wrap"><input type="number" required min="1" max="100000" step="any" value={target} onChange={event => { setTarget(Number(event.target.value)); onResult(null) }} /><em>LPH</em></div></label>
      </div></fieldset>
      {selectedSite && <p className="assessment-description">Recorded geology: <strong>{selectedSite.geology}</strong></p>}
      <div className="drilling-notice"><strong>Reference evidence, not a confirmed drilling outcome.</strong><p>Records cover 26 stations in 20 districts. Conditions at your plot may differ. Drilling success needs a local survey and a model trained on actual drilling outcomes.</p></div>
      <div className="form-actions"><button className="primary-button" disabled={busy || !selectedSite} type="submit">{busy ? 'Reviewing location…' : 'Review this location'} <span>→</span></button><button className="quiet-button" type="button" disabled={busy} onClick={() => { setDistrict(''); setSiteId(''); setTarget(0); onResult(null); setError('') }}>Reset fields</button></div>
      {error && <p className="error-banner" role="alert">{error}</p>}
    </form>
    <aside className="result-panel" aria-live="polite" data-spotlight="light"><span className="surface-glow" aria-hidden="true" />
      {result ? <SiteResultView result={result} /> : <div className="empty-result"><span className="result-kicker">Location evidence</span><div className="target-icon">◎</div><h2>Understand the groundwater nearby.</h2><p>Choose a district and reference station to see geology, water level and recorded discharge. Locations outside the listed coverage do not yet have usable reference data.</p></div>}
    </aside>
  </section>
}

function SiteResultView({ result }: { result: SiteResult }) {
  const [language, setLanguage] = useState<AssistantLanguage>('en')
  const [translated, setTranslated] = useState<{ key: string; text: string; error: boolean } | null>(null)
  const [retry, setRetry] = useState(0)
  const key = `${JSON.stringify(result)}:${language}:${retry}`
  const local = `${result.summary} ${result.next_step}`
  const settled = translated?.key === key
  useEffect(() => {
    if (language === 'en') return
    let current = true
    void sendChat([{ role: 'user', content: 'Explain this reference location evidence in simple words in the selected language. Distinguish the reference station from the proposed plot. Drilling success is unconfirmed; do not invent a probability or six-month drilling result. Mention the missing measurement date.' }], language, result)
      .then(text => { if (current) setTranslated({ key, text, error: false }) })
      .catch(() => { if (current) setTranslated({ key, text: '', error: true }) })
    return () => { current = false }
  }, [key, language, result])
  const maxYield = Math.max(result.reference_yield_lph, result.desired_yield_lph)
  return <div className="result-content">
    <p className="eyebrow">{result.site.mandal} / {result.site.district}</p>
    <h2>{result.site.station}</h2>
    <p className="drilling-outcome">New drilling success: <strong>Unconfirmed</strong></p>
    <div className="site-facts"><div><span>Recorded geology</span><strong>{result.site.geology}</strong></div><div><span>Reference water level</span><strong>{result.site.water_level_m} m below ground</strong><small>{result.reference_water_depth_ft} ft · not a recommended drilling depth</small></div></div>
    <div className="depth-chart" role="img" aria-label={`Reference discharge ${result.reference_yield_lph} litres per hour. Required yield ${result.desired_yield_lph} litres per hour.`}>
      <h3>Recorded discharge vs your requirement</h3>
      <p>Litres per hour · measured at the reference station</p>
      <div><span>Reference discharge</span><b>{result.reference_yield_lph.toLocaleString()} LPH</b><i style={{ width: `${result.reference_yield_lph / maxYield * 100}%` }} /></div>
      <div><span>Your water requirement</span><b>{result.desired_yield_lph.toLocaleString()} LPH</b><i className="water-depth" style={{ width: `${result.desired_yield_lph / maxYield * 100}%` }} /></div>
      <p>{result.evidence_status === 'reference_meets_target' ? 'The reference station meets your water requirement.' : 'The reference station records less discharge than you need.'} This does not predict the yield of a new borewell.</p>
    </div>
    <section className="result-explanation"><div className="explanation-heading"><h4>What this means</h4><label>Language<select value={language} onChange={event => setLanguage(event.target.value as AssistantLanguage)}>{resultLanguages.map(option => <option key={option.code} value={option.code}>{option.label}</option>)}</select></label></div>
      <p className="explanation-copy">{language === 'en' ? local : settled && translated.text ? translated.text : local}</p>
      {language !== 'en' && !settled && <p role="status">Preparing translation…</p>}
      {language !== 'en' && settled && translated.error && <div className="explanation-error" role="alert">Translation unavailable. Showing English.<button type="button" onClick={() => setRetry(value => value + 1)}>Retry</button></div>}
    </section>
    <p className="reference-source">Source: repository APT table · Measurement date not supplied.</p>
    <p className="assessment-description">{result.limitation}</p>
  </div>
}
