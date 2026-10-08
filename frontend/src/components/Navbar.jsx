import { NavLink, Link } from 'react-router-dom'
import { ShieldCheck, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Navbar(){
  const [open,setOpen]=useState(false)
  const links=[['/','Home'],['/analyze','Analyze'],['/scam-types','Scam Types'],['/history','History'],['/about','About']]
  return <header className="nav-wrap">
    <nav className="nav container">
      <Link to="/" className="brand" onClick={()=>setOpen(false)}>
        <span className="brand-mark"><ShieldCheck size={22}/></span>
        <span>Trust<span className="brand-accent">Shield</span></span>
      </Link>
      <button className="menu-btn" onClick={()=>setOpen(!open)} aria-label="Toggle navigation">{open?<X/>:<Menu/>}</button>
      <div className={`nav-links ${open?'open':''}`}>
        {links.map(([to,label])=><NavLink key={to} to={to} onClick={()=>setOpen(false)} className={({isActive})=>isActive?'active':''}>{label}</NavLink>)}
        <Link to="/analyze" onClick={()=>setOpen(false)} className="btn btn-sm btn-primary">Start Analysis</Link>
      </div>
    </nav>
  </header>
}
