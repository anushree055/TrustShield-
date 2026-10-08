import { ShieldCheck } from 'lucide-react'
export default function Footer(){
  return <footer className="footer">
    <div className="container footer-inner">
      <div><div className="brand footer-brand"><span className="brand-mark"><ShieldCheck size={18}/></span>Trust<span className="brand-accent">Shield</span></div><p className="muted">AI-powered scam detection and explainable risk intelligence.</p></div>
      <div className="footer-note">Academic PBL prototype · Always verify critical decisions through official channels.</div>
    </div>
  </footer>
}
