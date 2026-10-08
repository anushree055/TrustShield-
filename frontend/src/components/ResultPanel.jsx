import { AlertTriangle, ShieldCheck, Fingerprint, Search, ChevronDown, CircleCheck, ArrowRight, ScanSearch } from 'lucide-react'
import { useState } from 'react'
import RiskGauge from './RiskGauge'
import ManipulationChart from './ManipulationChart'
import RecoveryAssistant from './RecoveryAssistant'

export default function ResultPanel({result,onReset}){
  const [tech,setTech]=useState(false)
  if(!result) return null
  const patterns=result.manipulation?.patterns||[]
  return <section className="result-shell reveal">
    <div className="result-head card">
      <div><div className="eyebrow danger"><AlertTriangle size={14}/> Analysis complete</div><RiskGauge score={result.risk_score} level={result.risk_level}/></div>
      <div className="result-summary">
        <p className="kicker">LIKELY SCAM TYPE</p>
        <h2>{result.likely_scam_type}</h2>
        <div className="confidence"><span>Confidence</span><strong>{result.confidence}%</strong></div>
        {result.alternative_possible_type && <p className="muted small">Possible alternative: <b>{result.alternative_possible_type}</b></p>}
        <p className="lead-sm">{result.explanation}</p>
      </div>
    </div>

    <div className="result-grid">
      <article className="card section-card">
        <div className="section-title"><ScanSearch size={18}/><div><span>Threat intelligence</span><h3>Why TrustShield flagged this</h3></div></div>
        <div className="signal-list">{result.detected_signals?.map((s,i)=><div className="signal" key={i}><CircleCheck size={16}/><span>{s}</span></div>)}</div>
        {!!result.suspicious_phrases?.length && <><p className="mini-label">Suspicious phrases</p><div className="chips">{result.suspicious_phrases.map((p,i)=><span className="chip danger-chip" key={i}>{p}</span>)}</div></>}
      </article>

      <article className="card section-card">
        <div className="section-title"><Fingerprint size={18}/><div><span>Behavioral insight</span><h3>Scam Manipulation Fingerprint</h3></div></div>
        <p className="muted small">Dominant strategy: <b>{result.manipulation?.dominant_strategy}</b></p>
        <ManipulationChart data={patterns}/>
        <div className="bar-list">{patterns.slice(0,5).map(p=><div className="bar-row" key={p.key||p.label}><div className="bar-meta"><span>{p.label}</span><strong>{p.score}%</strong></div><div className="bar-track"><div className="bar-fill" style={{width:`${p.score}%`}}/></div></div>)}</div>
      </article>
    </div>

    <article className="card section-card action-card">
      <div className="section-title"><ShieldCheck size={19}/><div><span>Personal safety plan</span><h3>What should I do now?</h3></div></div>
      <div className="action-grid">{result.recommended_actions?.map((a,i)=><div className="action-item" key={i}><div className="action-num">{i+1}</div><div><h4>{a.title}</h4><p>{a.text}</p></div></div>)}</div>
    </article>

    <article className="card tech-card">
      <button className="tech-toggle" onClick={()=>setTech(!tech)}><span><Search size={17}/> View technical details</span><ChevronDown className={tech?'rot':''} size={18}/></button>
      {tech && <pre>{JSON.stringify(result.technical_details||{},null,2)}</pre>}
    </article>

    <RecoveryAssistant result={result} />

    <div className="result-actions"><button className="btn btn-primary" onClick={onReset}>Analyze another <ArrowRight size={17}/></button></div>
  </section>
}
