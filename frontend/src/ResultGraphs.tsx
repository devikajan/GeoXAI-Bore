import type { PredictionResult } from './api'

type ProbabilityBar = {
  label: string
  value: number
  className: string
}

export default function ResultGraphs({ result }: { result: PredictionResult }) {
  const score = result.ensemble_probability * 100
  const markerPosition = Math.min(100, Math.max(0, score))
  const bars: ProbabilityBar[] = [
    { label: 'Random Forest', value: result.random_forest_probability * 100, className: 'rf' },
    { label: 'XGBoost', value: result.xgboost_probability * 100, className: 'xgb' },
    { label: 'Ensemble', value: score, className: 'ensemble' },
  ]

  return (
    <section className="result-graphs" aria-labelledby="prediction-graphs-title">
      <div className="graph-heading">
        <h3 id="prediction-graphs-title">Prediction graphs</h3>
        <strong>{score.toFixed(1)} / 100</strong>
      </div>

      <div className="risk-scale" aria-label={`Risk score ${score.toFixed(1)} out of 100`}>
        <div className="risk-scale-labels"><span>Low</span><span>Medium</span><span>High</span></div>
        <div className="risk-scale-track">
          <i className="low" /><i className="medium" /><i className="high" />
          <b style={{ left: `${markerPosition}%` }}><span>{score.toFixed(1)}</span></b>
        </div>
      </div>

      <div className="probability-chart" aria-label="Model probability comparison">
        {bars.map((bar) => (
          <div className="probability-row" key={bar.label}>
            <span>{bar.label}</span>
            <div className="probability-track"><i className={bar.className} style={{ width: `${bar.value}%` }} /></div>
            <strong>{bar.value.toFixed(1)}%</strong>
          </div>
        ))}
      </div>
    </section>
  )
}
