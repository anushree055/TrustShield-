import { useMemo, useState } from 'react'
import { Search, ShieldCheck, AlertTriangle } from 'lucide-react'
import { scamTypes } from '../data/scams'

export default function ScamTypes(){
  const [q,setQ]=useState('')
  const filtered=useMemo(()=>scamTypes.filter(s=>(s.name+s.short+s.signs.join(' ')).toLowerCase().includes(q.toLowerCase())),[q])
  return <div className="container page-pad"><div className="page-heading single"><div><span className="eyebrow"><ShieldCheck size={14}/> Scam awareness library</span><h1>Know the pattern before it works on you.</h1><p>Simple explanations of common scam types, their warning signs and the safest response.</p></div></div><div className="search-box"><Search size={18}/><input placeholder="Search scam types or warning signs…" value={q} onChange={e=>setQ(e.target.value)}/></div><div className="scam-grid">{filtered.map(s=><article className="scam-card card" key={s.name}><div className="scam-icon">{s.icon}</div><h3>{s.name}</h3><p>{s.short}</p><div className="divider"/><h4><AlertTriangle size={15}/> Common warning signs</h4><ul>{s.signs.map(x=><li key={x}>{x}</li>)}</ul><div className="protect"><ShieldCheck size={16}/><span>{s.protect}</span></div></article>)}</div></div>
}
