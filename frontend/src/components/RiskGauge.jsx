export default function RiskGauge({score=0, level='Unknown'}){
  const circumference=2*Math.PI*54
  const offset=circumference-(Math.max(0,Math.min(100,score))/100)*circumference
  return <div className="gauge-wrap">
    <svg className="gauge" viewBox="0 0 128 128" aria-label={`Risk score ${score} out of 100`}>
      <circle cx="64" cy="64" r="54" className="gauge-track" />
      <circle cx="64" cy="64" r="54" className="gauge-value" strokeDasharray={circumference} strokeDashoffset={offset}/>
    </svg>
    <div className="gauge-center"><strong>{score}</strong><span>/ 100</span><em>{level}</em></div>
  </div>
}
