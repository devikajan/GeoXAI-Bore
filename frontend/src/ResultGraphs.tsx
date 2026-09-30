import type { PredictionResult } from './api'

type ProbabilityBar = {
  label: string
  value: number
  className: string
}

export default function ResultGraphs({ result }: { result: PredictionResult }) {
  const score = result.ensemble_probability * 100
  const categoryClass = result.risk_category.toLowerCase()
  const markerPosition = Math.min(100, Math.max(0, score))
  const maximumImpact = Math.max(...result.top_features.map((feature) => Math.abs(feature.shap_value)), 0.001)
  const bars: ProbabilityBar[] = [
    { label: 'Random Forest', value: result.random_forest_probability * 100, className: 'rf' },
    { label: 'XGBoost', value: result.xgboost_probability * 100, className: 'xgb' },
    { label: 'Ensemble', value: score, className: 'ensemble' },
  ]
  const riskExplanation = {
    Low: 'The current measurements indicate a lower predicted chance of failure. Continue normal monitoring and maintenance.',
    Medium: 'The measurements show a moderate predicted chance of failure. Review the main risk factors and plan an inspection.',
    High: 'The measurements indicate an elevated predicted chance of failure. Prioritize inspection by a qualified technician.',
  }[result.risk_category]

  return (
    <section className="result-graphs" aria-labelledby="risk-analysis-title">
      <div className="graph-heading">
        <div><span>Six-month prediction</span><h3 id="risk-analysis-title">Risk analysis</h3></div>
        <div className={`risk-score-badge ${categoryClass}`}><strong>{score.toFixed(1)}</strong><span>/ 100</span></div>
      </div>
      <p className="risk-explanation"><strong>{result.risk_category} risk.</strong> {riskExplanation}</p>

      <div className="risk-scale" aria-label={`Risk score ${score.toFixed(1)} out of 100`}>
        <div className="risk-scale-labels"><span>Low</span><span>Medium</span><span>High</span></div>
        <div className="risk-scale-track">
          <i className="low" /><i className="medium" /><i className="high" />
          <b style={{ left: `${markerPosition}%` }}><span>{score.toFixed(1)}</span></b>
        </div>
      </div>

      <div className="chart-block">
        <div className="chart-title"><h4>Model agreement</h4><span>Predicted failure probability</span></div>
        <div className="probability-chart" aria-label="Model probability comparison">
          {bars.map((bar) => (
            <div className="probability-row" key={bar.label}>
              <span>{bar.label}</span>
              <div className="probability-track"><i className={bar.className} style={{ width: `${bar.value}%` }} /></div>
              <strong>{bar.value.toFixed(1)}%</strong>
            </div>
          ))}
        </div>
      </div>

      {result.top_features.length > 0 && (
        <div className="chart-block">
          <div className="chart-title"><h4>Why this result?</h4><span>SHAP model influence</span></div>
          <p className="chart-help">Green factors reduce the prediction. Red factors increase it.</p>
          <div className="impact-chart" aria-label="SHAP feature influence graph">
            <div className="impact-legend"><span>Reduces risk</span><span>Increases risk</span></div>
            {result.top_features.map((feature) => {
              const positive = feature.shap_value >= 0
              const width = `${(Math.abs(feature.shap_value) / maximumImpact) * 100}%`
              return (
                <div className="impact-row" key={feature.feature}>
                  <span title={feature.feature}>{formatFeatureName(feature.feature)}</span>
                  <div className="impact-axis">
                    <div>{!positive && <i className="negative" style={{ width }} />}</div>
                    <div>{positive && <i className="positive" style={{ width }} />}</div>
                  </div>
                  <strong className={positive ? 'positive-text' : 'negative-text'}>
                    {positive ? '+' : ''}{feature.shap_value.toFixed(3)}
                  </strong>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}

function formatFeatureName(feature: string) {
  return feature
    .replace(/^(categorical|numerical)__/, '')
    .replace(/_/g, ' ')
    .replace(/\b(ft|lph|mm|mms|pct)\b/gi, (unit) => unit.toUpperCase())
}
