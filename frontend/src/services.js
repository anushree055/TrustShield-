const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

async function parse(res) {
  if (!res.ok) {
    let msg = 'Something went wrong.'
    try { const data = await res.json(); msg = data.detail || data.message || msg } catch {}
    throw new Error(msg)
  }
  return res.json()
}

export async function analyzeUrl(url) {
  return parse(await fetch(`${API}/analyze/url`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url})}))
}
export async function analyzeMessage(text) {
  return parse(await fetch(`${API}/analyze/message`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text})}))
}
export async function analyzeFull(url, text) {
  return parse(await fetch(`${API}/analyze/full`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url:url||null,text:text||null})}))
}
export async function analyzeScreenshot(file) {
  const form = new FormData(); form.append('file', file)
  return parse(await fetch(`${API}/analyze/screenshot`, {method:'POST', body:form}))
}
export async function getHistory() { return parse(await fetch(`${API}/history`)) }
export async function getStats() { return parse(await fetch(`${API}/stats`)) }
export async function deleteHistoryItem(id) { return parse(await fetch(`${API}/history/${id}`, {method:'DELETE'})) }
export async function clearHistory() { return parse(await fetch(`${API}/history`, {method:'DELETE'})) }

/**
 * POST /api/recovery
 * @param {object} payload  { analysis_id, scam_type, risk_score, signals, interactions, follow_ups }
 */
export async function callRecovery(payload) {
  return parse(await fetch(`${API}/recovery`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
}
