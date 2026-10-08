import { useEffect, useState } from 'react'
import { History as HistoryIcon, Trash2, RefreshCw, ShieldAlert, Activity, BarChart3, Layers3 } from 'lucide-react'
import { getHistory, getStats, deleteHistoryItem, clearHistory } from '../services'

export default function History(){
 const [rows,setRows]=useState([]),[stats,setStats]=useState({}),[loading,setLoading]=useState(true),[filter,setFilter]=useState('All')
 async function load(){setLoading(true);try{const [r,s]=await Promise.all([getHistory(),getStats()]);setRows(r);setStats(s)}finally{setLoading(false)}}
 useEffect(()=>{load()},[])
 const shown=filter==='All'?rows:rows.filter(r=>r.input_type===filter)
 return <div className="container page-pad"><div className="page-heading"><div><span className="eyebrow"><HistoryIcon size={14}/> Local analysis history</span><h1>Your recent TrustShield scans</h1><p>Review the risk score and likely scam category from previous local analyses.</p></div><button className="btn btn-ghost" onClick={load}><RefreshCw size={16}/> Refresh</button></div>
 <div className="metric-grid"><div className="metric card"><Layers3/><span>Total analyses</span><strong>{stats.total??'—'}</strong></div><div className="metric card"><ShieldAlert/><span>High risk</span><strong>{stats.high_risk??'—'}</strong></div><div className="metric card"><Activity/><span>Average risk</span><strong>{stats.average_risk??'—'}</strong></div><div className="metric card"><BarChart3/><span>Most common</span><strong className="metric-text">{stats.most_common_scam??'—'}</strong></div></div>
 <div className="history-toolbar"><div className="filter-pills">{['All','URL','Message','Screenshot','Full Analysis'].map(x=><button className={filter===x?'active':''} onClick={()=>setFilter(x)} key={x}>{x}</button>)}</div><button className="btn btn-danger" onClick={async()=>{if(confirm('Clear all analysis history?')){await clearHistory();load()}}}><Trash2 size={15}/> Clear history</button></div>
 <div className="history-list card">{loading?<div className="empty">Loading history…</div>:shown.length===0?<div className="empty">No analyses yet. Run a scan to see it here.</div>:shown.map(r=><div className="history-row" key={r.id}><div className="risk-dot"><span>{r.risk_score}</span></div><div className="history-main"><div className="history-top"><b>{r.scam_type}</b><span>{r.input_type}</span></div><p>{r.input_preview}</p><small>{new Date(r.created_at).toLocaleString()} · {r.risk_level} · {r.confidence}% confidence</small></div><button className="icon-btn" onClick={async()=>{await deleteHistoryItem(r.id);load()}} aria-label="Delete"><Trash2 size={16}/></button></div>)}</div></div>
}
