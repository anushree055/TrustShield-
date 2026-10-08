import { Link } from 'react-router-dom'
import { ArrowRight, ShieldCheck, Link2, MessageSquareText, Image, Fingerprint, ScanSearch, Sparkles, LockKeyhole, Activity, CheckCircle2 } from 'lucide-react'

const features=[
  {icon:<Link2/>,title:'URL Analyzer',text:'Inspect suspicious links for phishing-style structure, bait words and risky URL signals.'},
  {icon:<MessageSquareText/>,title:'Message Analyzer',text:'Analyze SMS, email or chat content for scam language, payment pressure and credential requests.'},
  {icon:<Image/>,title:'Screenshot Analyzer',text:'Upload a screenshot, extract its text with OCR and run the same explainable scam analysis.'},
  {icon:<Fingerprint/>,title:'Manipulation Fingerprint',text:'See whether urgency, fear, authority, reward or credential pressure is being used against you.'},
]
export default function Home(){
  return <>
    <section className="hero container">
      <div className="hero-copy reveal">
        <div className="eyebrow"><Sparkles size={14}/> Explainable scam intelligence</div>
        <h1>Check before<br/><span>you trust.</span></h1>
        <p>TrustShield analyzes suspicious links, messages and screenshots, identifies the likely scam type, explains the warning signs and tells you what to do next.</p>
        <div className="hero-actions"><Link to="/analyze" className="btn btn-primary">Analyze a Scam <ArrowRight size={17}/></Link><Link to="/scam-types" className="btn btn-ghost">Explore Scam Types</Link></div>
        <div className="trust-row"><CheckCircle2 size={16}/><span>No fake random scores</span><CheckCircle2 size={16}/><span>Explainable signals</span><CheckCircle2 size={16}/><span>Beginner-friendly safety advice</span></div>
      </div>
      <div className="hero-visual reveal">
        <div className="shield-orbit"><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="shield-core"><ShieldCheck size={56}/><span>TRUSTSHIELD</span></div></div>
        <div className="float-card fc-one"><ScanSearch size={17}/><div><span>Threat scan</span><b>12 signals checked</b></div></div>
        <div className="float-card fc-two"><LockKeyhole size={17}/><div><span>Risk engine</span><b>Explainable scoring</b></div></div>
        <div className="float-card fc-three"><Activity size={17}/><div><span>Status</span><b className="safe-text">Ready to analyze</b></div></div>
      </div>
    </section>

    <section className="stats-strip container">
      <div><strong>10+</strong><span>Scam categories</span></div><div><strong>4</strong><span>Analysis modes</span></div><div><strong>8</strong><span>Manipulation signals</span></div><div><strong>5</strong><span>Action steps per result</span></div>
    </section>

    <section className="section container"><div className="section-heading"><span className="eyebrow">MULTI-MODAL PROTECTION</span><h2>One platform. Multiple scam signals.</h2><p>Designed to make scam detection understandable, not mysterious.</p></div><div className="feature-grid">{features.map((f,i)=><article className="feature-card card" key={f.title}><div className="feature-icon">{f.icon}</div><span className="feature-index">0{i+1}</span><h3>{f.title}</h3><p>{f.text}</p></article>)}</div></section>

    <section className="section container"><div className="workflow card"><div className="workflow-copy"><span className="eyebrow">HOW IT WORKS</span><h2>From suspicious content to a clear action plan.</h2><p>TrustShield combines structural signals, text classification and transparent rule-based indicators to produce a readable result.</p><Link to="/analyze" className="text-link">Run a demo analysis <ArrowRight size={15}/></Link></div><div className="steps">{[['01','Submit','Paste a URL/message or upload a screenshot.'],['02','Analyze','Threat signals and manipulation patterns are extracted.'],['03','Understand','See the likely scam type and why it was flagged.'],['04','Act safely','Get scam-specific next steps and recovery advice.']].map(x=><div className="step" key={x[0]}><span>{x[0]}</span><div><h4>{x[1]}</h4><p>{x[2]}</p></div></div>)}</div></div></section>

    <section className="section container"><div className="cta card"><div><span className="eyebrow">READY WHEN YOU ARE</span><h2>Suspicious message? Check it before you react.</h2><p>Use a demo example or paste your own content.</p></div><Link to="/analyze" className="btn btn-primary">Start Analysis <ArrowRight size={17}/></Link></div></section>
  </>
}
