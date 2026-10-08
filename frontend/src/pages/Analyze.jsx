import { useMemo, useState } from 'react'
import { Link2, MessageSquareText, Image as ImageIcon, Layers3, UploadCloud, Sparkles, LoaderCircle, AlertCircle, FileText, WandSparkles } from 'lucide-react'
import { analyzeUrl, analyzeMessage, analyzeFull, analyzeScreenshot } from '../services'
import ResultPanel from '../components/ResultPanel'
import { demoMessages } from '../data/scams'

const tabs=[['url','URL',Link2],['message','Message',MessageSquareText],['screenshot','Screenshot',ImageIcon],['full','Full Analysis',Layers3]]
const loadingSteps=['Scanning submitted content…','Extracting risk indicators…','Identifying scam pattern…','Analyzing manipulation techniques…','Generating safety recommendations…']

export default function Analyze(){
  const [tab,setTab]=useState('message'), [url,setUrl]=useState(''), [text,setText]=useState(''), [file,setFile]=useState(null), [preview,setPreview]=useState(''), [result,setResult]=useState(null), [loading,setLoading]=useState(false), [error,setError]=useState(''), [step,setStep]=useState(0), [ocrText,setOcrText]=useState('')
  const canAnalyze=useMemo(()=>tab==='url'?url.trim():tab==='message'?text.trim():tab==='screenshot'?!!file:(url.trim()||text.trim()),[tab,url,text,file])

  async function run(){
    setLoading(true);setError('');setResult(null);setStep(0)
    const timer=setInterval(()=>setStep(s=>Math.min(loadingSteps.length-1,s+1)),450)
    try{
      let data
      if(tab==='url') data=await analyzeUrl(url)
      if(tab==='message') data=await analyzeMessage(text)
      if(tab==='full') data=await analyzeFull(url,text)
      if(tab==='screenshot'){
        data=await analyzeScreenshot(file)
        if(data.ocr_text) setOcrText(data.ocr_text)
        if(data.ocr_success===false){ setError(data.message); return }
      }
      setResult(data)
      setTimeout(()=>document.getElementById('results')?.scrollIntoView({behavior:'smooth',block:'start'}),100)
    } catch(e){setError(e.message)} finally{clearInterval(timer);setLoading(false)}
  }
  function pickFile(e){const f=e.target.files?.[0]; if(!f)return; setFile(f);setPreview(URL.createObjectURL(f));setOcrText('')}
  function loadDemo(name){setTab('message');setText(demoMessages[name]);setResult(null);window.scrollTo({top:260,behavior:'smooth'})}
  function reset(){setResult(null);setError('');setOcrText('');window.scrollTo({top:0,behavior:'smooth'})}

  return <div className="container page-pad">
    <div className="page-heading"><div><span className="eyebrow"><Sparkles size={14}/> TrustShield analyzer</span><h1>Analyze suspicious content</h1><p>Choose an input type. TrustShield will explain the risk, likely scam type, manipulation strategy and next steps.</p></div><div className="demo-select"><span>Quick demo</span><select defaultValue="" onChange={e=>e.target.value&&loadDemo(e.target.value)}><option value="" disabled>Choose an example</option>{Object.keys(demoMessages).map(k=><option key={k}>{k}</option>)}</select></div></div>

    <section className="analyzer card">
      <div className="tabs">{tabs.map(([id,label,Icon])=><button key={id} onClick={()=>{setTab(id);setResult(null);setError('')}} className={tab===id?'active':''}><Icon size={17}/>{label}</button>)}</div>
      <div className="analyzer-body">
        {tab==='url' && <div className="input-stack"><label>Suspicious URL</label><div className="url-input"><Link2 size={18}/><input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com/login"/></div><p className="hint">Tip: You can paste a complete link or a domain. TrustShield checks structure, bait words and model signals.</p></div>}
        {tab==='message' && <div className="input-stack"><div className="label-row"><label>Message, SMS or email text</label><span>{text.length}/20,000</span></div><textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Paste the suspicious message here…" rows={10}/><p className="hint">Try a bank warning, job offer, OTP request, prize message or a normal safe message.</p></div>}
        {tab==='screenshot' && <div className="input-stack"><label>Upload screenshot</label><label className="drop-zone"><input type="file" accept="image/png,image/jpeg,image/webp" onChange={pickFile}/>{preview?<img src={preview} alt="Screenshot preview"/>:<><UploadCloud size={34}/><strong>Drop or choose a screenshot</strong><span>PNG · JPG · WEBP · max 8 MB</span></>}</label>{ocrText&&<><div className="label-row"><label>Extracted text</label><span>OCR preview</span></div><textarea value={ocrText} onChange={e=>setOcrText(e.target.value)} rows={6}/><button className="btn btn-ghost" onClick={async()=>{setLoading(true);try{setResult(await analyzeMessage(ocrText))}catch(e){setError(e.message)}finally{setLoading(false)}}}><FileText size={16}/> Analyze edited text</button></>}</div>}
        {tab==='full' && <div className="split-input"><div className="input-stack"><label>URL (optional)</label><div className="url-input"><Link2 size={18}/><input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://…"/></div></div><div className="input-stack"><label>Message (optional)</label><textarea value={text} onChange={e=>setText(e.target.value)} rows={8} placeholder="Paste related message…"/></div></div>}
        {error&&<div className="error-box"><AlertCircle size={18}/>{error}</div>}
        <div className="analyze-row"><div className="privacy-note">Your analysis is stored only in the local project database for demo history.</div><button className="btn btn-primary btn-lg" disabled={!canAnalyze||loading} onClick={run}>{loading?<><LoaderCircle className="spin" size={18}/>{loadingSteps[step]}</>:<><WandSparkles size={18}/>Analyze with TrustShield</>}</button></div>
      </div>
    </section>
    <div id="results"><ResultPanel result={result} onReset={reset}/></div>
  </div>
}
