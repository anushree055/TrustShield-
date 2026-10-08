import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'

export default function ManipulationChart({data=[]}){
  const active=(data||[]).slice(0,8).map(x=>({name:x.label.replace(' Pressure',''),score:x.score||0}))
  if(!active.length) return null
  return <div className="radar-box">
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={active} outerRadius="68%">
        <PolarGrid stroke="rgba(139,170,201,.18)" />
        <PolarAngleAxis dataKey="name" tick={{fill:'#9fb4c9',fontSize:11}} />
        <Radar dataKey="score" stroke="#5eead4" fill="#5eead4" fillOpacity={0.18} />
      </RadarChart>
    </ResponsiveContainer>
  </div>
}
