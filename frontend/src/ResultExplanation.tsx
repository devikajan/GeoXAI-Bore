import { useEffect, useState } from 'react'
import { sendChat } from './api'
import type { PredictionResult } from './api'

import { resultLanguages } from './resultLanguages'
import type { ResultLanguage } from './resultLanguages'

export default function ResultExplanation({ result }: { result: PredictionResult }) {
  const [language, setLanguage] = useState<ResultLanguage>('en')
  const [retry, setRetry] = useState(0)
  const [response, setResponse] = useState<{ key: string; text: string; error: string } | null>(null)
  const resultKey = `${result.ensemble_probability}:${result.risk_category}:${result.top_features.map((feature) => `${feature.feature}:${feature.shap_value}`).join('|')}`
  const requestKey = `${resultKey}:${language}:${retry}`
  const settled = response?.key === requestKey
  const loading = !settled
  const explanation = settled ? response.text : language === 'en' ? localExplanation(result) : ''
  const error = settled ? response.error : ''

  useEffect(() => {
    let current = true
    const prompt = [
      'Explain the attached borewell assessment in simple words for a non-technical reader.',
      'State the predicted six-month failure score out of 100 and what the risk category means.',
      'Describe up to three strongest SHAP factors as model influences that increase or reduce risk.',
      'End with one practical next step. Do not invent measurements or causes. Keep it under 130 words.',
    ].join(' ')

    void sendChat([{ role: 'user', content: prompt }], language, result)
      .then((reply) => { if (current) setResponse({ key: requestKey, text: reply, error: '' }) })
      .catch(() => {
        if (!current) return
        setResponse({
          key: requestKey,
          text: language === 'en' ? localExplanation(result) : '',
          error: language === 'en'
            ? 'The AI explanation is temporarily unavailable. The summary below is based directly on the model result.'
            : 'This translation is temporarily unavailable. Please retry or choose English.',
        })
      })

    return () => { current = false }
  }, [language, requestKey, result])

  return (
    <section className="result-explanation" aria-labelledby="plain-explanation-title">
      <div className="explanation-heading">
        <div><span>Plain-language summary</span><h4 id="plain-explanation-title">What this result means</h4></div>
        <label>Language
          <select value={language} onChange={(event) => setLanguage(event.target.value as ResultLanguage)}>
            {resultLanguages.map((option) => <option key={option.code} value={option.code}>{option.label}</option>)}
          </select>
        </label>
      </div>
      {loading && <p className="explanation-status" role="status">Preparing the explanation…</p>}
      {explanation && <p className="explanation-copy">{explanation}</p>}
      {error && <div className="explanation-error" role="alert"><span>{error}</span><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>}
    </section>
  )
}

function localExplanation(result: PredictionResult) {
  const score = (result.ensemble_probability * 100).toFixed(1)
  const meaning = {
    Low: 'The model sees a lower predicted chance of failure, so routine monitoring and maintenance are appropriate.',
    Medium: 'The model sees a moderate predicted chance of failure, so the main warning factors should be reviewed and an inspection planned.',
    High: 'The model sees an elevated predicted chance of failure, so a qualified technician should inspect the borewell soon.',
  }[result.risk_category]
  const factors = result.top_features.slice(0, 3).map((feature) =>
    `${formatFeatureName(feature.feature)} ${feature.shap_value >= 0 ? 'increases' : 'reduces'} the model's risk estimate`,
  )
  const factorSentence = factors.length ? ` The strongest signals are: ${factors.join('; ')}.` : ''
  return `The predicted chance of failure within six months is ${score} out of 100, classified as ${result.risk_category.toLowerCase()} risk. ${meaning}${factorSentence}`
}

function formatFeatureName(feature: string) {
  return feature.replace(/^(categorical|numerical)__/, '').replace(/_/g, ' ')
}
