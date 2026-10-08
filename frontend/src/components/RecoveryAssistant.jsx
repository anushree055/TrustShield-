/**
 * RecoveryAssistant.jsx
 * ---------------------
 * "I Already Interacted With This" post-analysis recovery panel.
 *
 * Usage:  <RecoveryAssistant result={analysisResult} />
 *
 * Props:
 *   result  – the full analysis result object from the backend
 */

import { useState } from 'react'
import {
  AlertTriangle, ShieldAlert, CheckCircle2, ChevronDown, ChevronUp,
  Loader2, Lock, CreditCard, Smartphone, Eye, FileWarning,
  HeartHandshake, Activity, ClipboardList, Info, ArrowRight,
  XCircle, Zap, BadgeAlert
} from 'lucide-react'
import { callRecovery } from '../services'

// ─── Interaction options shown as selectable cards ───────────────────────────
const INTERACTION_OPTIONS = [
  { key: 'clicked_link',        icon: '🔗', label: 'I clicked the link',                          short: 'Clicked link' },
  { key: 'entered_credentials', icon: '🔑', label: 'I entered a username or password',             short: 'Entered password' },
  { key: 'shared_otp',          icon: '📲', label: 'I shared an OTP',                             short: 'Shared OTP' },
  { key: 'shared_pin_cvv',      icon: '💳', label: 'I shared a PIN, CVV, or card details',        short: 'Shared PIN/CVV' },
  { key: 'entered_bank_upi',    icon: '🏦', label: 'I entered bank account or UPI details',       short: 'Bank/UPI details' },
  { key: 'sent_money',          icon: '💸', label: 'I approved or sent a payment',                short: 'Sent money' },
  { key: 'downloaded_file',     icon: '📥', label: 'I downloaded a file',                         short: 'Downloaded file' },
  { key: 'installed_app',       icon: '📱', label: 'I installed an application',                  short: 'Installed app' },
  { key: 'gave_remote_access',  icon: '🖥️', label: 'I gave remote-access permission',            short: 'Remote access' },
  { key: 'shared_identity',     icon: '🪪', label: 'I shared personal identity information',      short: 'Shared identity',
    hint: 'e.g. Aadhaar, PAN, passport, date of birth, address, or document image' },
  { key: 'replied_only',        icon: '💬', label: 'I only replied to the sender',                short: 'Replied' },
  { key: 'not_sure',            icon: '❓', label: "I'm not sure what I did",                    short: 'Not sure' },
]

// ─── Follow-up question definitions ─────────────────────────────────────────
const FOLLOW_UPS = {
  clicked_link: {
    id: 'entered_after_click',
    question: 'Did you enter any information after opening the link?',
    options: [
      { value: 'no',       label: 'No, I just looked' },
      { value: 'yes',      label: 'Yes, I entered something' },
      { value: 'not_sure', label: 'Not sure' },
    ]
  },
  entered_credentials: {
    id: 'password_reused',
    question: 'Do you use this same password on any other account?',
    options: [
      { value: 'yes',      label: 'Yes' },
      { value: 'no',       label: 'No, it is unique' },
      { value: 'not_sure', label: 'Not sure' },
    ]
  },
  shared_otp: {
    id: 'otp_service',
    question: 'What service was the OTP related to?',
    options: [
      { value: 'banking',  label: 'Banking' },
      { value: 'upi',      label: 'UPI / Payments' },
      { value: 'login',    label: 'Account login' },
      { value: 'other',    label: 'Other service' },
      { value: 'not_sure', label: 'Not sure' },
    ]
  },
  sent_money: {
    id: 'payment_method',
    question: 'How was the payment made?',
    options: [
      { value: 'upi',         label: 'UPI' },
      { value: 'debit_card',  label: 'Debit Card' },
      { value: 'credit_card', label: 'Credit Card' },
      { value: 'bank_transfer', label: 'Bank Transfer' },
      { value: 'wallet',      label: 'Wallet' },
      { value: 'other',       label: 'Other' },
    ]
  },
  installed_app: {
    id: 'app_type',
    question: 'What kind of application was it?',
    options: [
      { value: 'remote_access', label: 'Remote access app (AnyDesk, TeamViewer, etc.)' },
      { value: 'apk',           label: 'APK / sideloaded app' },
      { value: 'unknown',       label: "Unknown / I'm not sure" },
      { value: 'other',         label: 'Other' },
    ]
  },
  gave_remote_access: {
    id: 'remote_app',
    question: 'Which remote-access tool was used?',
    options: [
      { value: 'anydesk',     label: 'AnyDesk' },
      { value: 'teamviewer',  label: 'TeamViewer' },
      { value: 'quicksupport',label: 'QuickSupport' },
      { value: 'screen_share',label: 'Screen sharing (WhatsApp, Meet, etc.)' },
      { value: 'other',       label: 'Other' },
    ]
  },
}

// ─── Severity styling ────────────────────────────────────────────────────────
const SEVERITY_CONFIG = {
  LOW:      { label: 'Low Exposure',      color: 'sev-low',      icon: CheckCircle2 },
  MODERATE: { label: 'Moderate Exposure', color: 'sev-moderate', icon: AlertTriangle },
  HIGH:     { label: 'High Exposure',     color: 'sev-high',     icon: ShieldAlert },
  CRITICAL: { label: 'Critical',          color: 'sev-critical', icon: XCircle },
}

// ─── Action section definitions (icon + heading) ────────────────────────────
const ACTION_SECTIONS = [
  { key: 'immediate_actions',  Icon: Zap,           heading: 'Immediate Actions',      sub: 'Do these first — right now.' },
  { key: 'account_security',   Icon: Lock,          heading: 'Secure Your Account',    sub: 'Prevent further unauthorised access.' },
  { key: 'financial_actions',  Icon: CreditCard,    heading: 'Financial Protection',   sub: 'Protect your money and payment methods.' },
  { key: 'device_actions',     Icon: Smartphone,    heading: 'Device Security',        sub: 'Clean and harden your device.' },
  { key: 'identity_actions',   Icon: Eye,           heading: 'Identity Protection',    sub: 'Guard against identity misuse.' },
  { key: 'reporting_actions',  Icon: FileWarning,   heading: 'Report the Incident',    sub: 'Create a record and alert authorities.' },
  { key: 'monitoring_actions', Icon: Activity,      heading: 'Stay Vigilant',          sub: 'Watch for follow-up threats.' },
]

// ─── Demo scenarios ──────────────────────────────────────────────────────────
const DEMO_SCENARIOS = [
  {
    label: 'Scenario 1: Clicked link only',
    interactions: ['clicked_link'],
    followUps: { entered_after_click: 'no' },
  },
  {
    label: 'Scenario 2: Entered password + shared OTP',
    interactions: ['entered_credentials', 'shared_otp'],
    followUps: { password_reused: 'yes', otp_service: 'banking' },
  },
  {
    label: 'Scenario 3: Installed remote-access app + sent money',
    interactions: ['installed_app', 'gave_remote_access', 'sent_money'],
    followUps: { app_type: 'remote_access', remote_app: 'anydesk', payment_method: 'upi' },
  },
]

// ─────────────────────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────────────────────
export default function RecoveryAssistant({ result }) {
  const [open, setOpen]               = useState(false)   // is panel expanded?
  const [selected, setSelected]       = useState([])      // selected interaction keys
  const [followUps, setFollowUps]     = useState({})      // follow-up answers
  const [step, setStep]               = useState('select') // 'select' | 'followup' | 'result'
  const [plan, setPlan]               = useState(null)
  const [loading, setLoading]         = useState(false)
  const [err, setErr]                 = useState('')
  const [expandedSections, setExpandedSections] = useState({})

  if (!result) return null

  // ── Which follow-up questions are relevant to current selections ──────────
  const activeFollowUps = Object.entries(FOLLOW_UPS).filter(
    ([key]) => selected.includes(key)
  )

  // ── Toggle interaction selection ─────────────────────────────────────────
  function toggleSelect(key) {
    setSelected(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    )
  }

  // ── Submit to backend ────────────────────────────────────────────────────
  async function submitRecovery() {
    setLoading(true)
    setErr('')
    try {
      const data = await callRecovery({
        analysis_id: result.analysis_id ?? null,
        scam_type  : result.likely_scam_type ?? 'Unknown',
        risk_score : result.risk_score ?? 50,
        signals    : result.detected_signals ?? [],
        interactions: selected,
        follow_ups : followUps,
      })
      setPlan(data)
      setStep('result')
      // expand the first two sections by default
      const initial = {}
      ACTION_SECTIONS.slice(0, 2).forEach(s => { initial[s.key] = true })
      setExpandedSections(initial)
      setTimeout(() => document.getElementById('recovery-result')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
    } catch (e) {
      setErr(e.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // ── Load a demo scenario ─────────────────────────────────────────────────
  function loadDemo(scenario) {
    setSelected(scenario.interactions)
    setFollowUps(scenario.followUps)
    setStep('select')
    setPlan(null)
    setErr('')
    setOpen(true)
  }

  // ── Reset ────────────────────────────────────────────────────────────────
  function reset() {
    setSelected([])
    setFollowUps({})
    setStep('select')
    setPlan(null)
    setErr('')
  }

  // ── Toggle action section expansion ──────────────────────────────────────
  function toggleSection(key) {
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const sevCfg = plan ? (SEVERITY_CONFIG[plan.severity] || SEVERITY_CONFIG.LOW) : null

  return (
    <article className="card recovery-trigger-card" id="recovery-section">
      {/* ── Trigger header ────────────────────────────────────────────────── */}
      <div className="recovery-trigger-row">
        <div className="recovery-trigger-copy">
          <div className="recovery-trigger-badge">
            <HeartHandshake size={15} />
            Recovery Assistant
          </div>
          <h3 className="recovery-trigger-heading">Already interacted with this?</h3>
          <p className="recovery-trigger-sub">
            If you clicked, shared information, sent money, or installed something,
            tell us what happened so TrustShield can suggest the next safest steps.
          </p>
        </div>
        <div className="recovery-trigger-actions">
          {/* Demo scenarios */}
          <div className="recovery-demo-row">
            <span className="mini-label">Demo scenarios</span>
            <div className="recovery-demo-btns">
              {DEMO_SCENARIOS.map((s, i) => (
                <button
                  key={i}
                  className="btn btn-ghost btn-sm recovery-demo-btn"
                  onClick={() => loadDemo(s)}
                  title={s.label}
                >
                  {`S${i + 1}`}
                </button>
              ))}
            </div>
          </div>
          <button
            className="btn btn-recovery-open"
            onClick={() => { setOpen(o => !o); if (!open) reset() }}
          >
            {open ? <><ChevronUp size={16} /> Close</> : <><HeartHandshake size={16} /> I already interacted</>}
          </button>
        </div>
      </div>

      {/* ── Expanded panel ────────────────────────────────────────────────── */}
      {open && (
        <div className="recovery-panel">
          {/* Privacy note */}
          <div className="recovery-privacy-note">
            <Info size={14} />
            <span>
              <strong>Privacy:</strong> TrustShield does not need your actual password,
              OTP, PIN, or card details. <em>Never enter those values here</em> — only
              tell us what category of information was involved.
            </span>
          </div>

          {/* ── STEP: SELECT interactions ─────────────────────────────────── */}
          {step !== 'result' && (
            <>
              <div className="recovery-section-header">
                <ClipboardList size={16} />
                <span>What did you do? Select all that apply.</span>
              </div>
              <div className="recovery-options-grid">
                {INTERACTION_OPTIONS.map(opt => (
                  <button
                    key={opt.key}
                    className={`recovery-option-card ${selected.includes(opt.key) ? 'selected' : ''}`}
                    onClick={() => toggleSelect(opt.key)}
                    aria-pressed={selected.includes(opt.key)}
                  >
                    <span className="recovery-option-icon">{opt.icon}</span>
                    <span className="recovery-option-label">{opt.label}</span>
                    {opt.hint && <span className="recovery-option-hint">{opt.hint}</span>}
                    {selected.includes(opt.key) && (
                      <CheckCircle2 className="recovery-check" size={15} />
                    )}
                  </button>
                ))}
              </div>

              {/* ── Follow-up questions ───────────────────────────────────── */}
              {activeFollowUps.length > 0 && (
                <div className="recovery-followups">
                  <div className="recovery-section-header">
                    <BadgeAlert size={16} />
                    <span>A few more questions — these help us give better advice. (Optional)</span>
                  </div>
                  {activeFollowUps.map(([interactionKey, fup]) => (
                    <div key={fup.id} className="recovery-followup-block">
                      <p className="recovery-followup-q">{fup.question}</p>
                      <div className="recovery-followup-opts">
                        {fup.options.map(opt => (
                          <button
                            key={opt.value}
                            className={`recovery-followup-btn ${followUps[fup.id] === opt.value ? 'active' : ''}`}
                            onClick={() => setFollowUps(prev => ({ ...prev, [fup.id]: opt.value }))}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {err && (
                <div className="error-box" style={{ marginTop: '14px' }}>
                  <AlertTriangle size={16} />
                  {err}
                </div>
              )}

              <div className="recovery-submit-row">
                <button
                  className="btn btn-primary"
                  disabled={selected.length === 0 || loading}
                  onClick={submitRecovery}
                >
                  {loading
                    ? <><Loader2 className="spin" size={16} /> Generating recovery plan…</>
                    : <><ArrowRight size={16} /> Get my recovery steps</>
                  }
                </button>
                {selected.length > 0 && (
                  <button className="btn btn-ghost btn-sm" onClick={reset}>
                    Clear selection
                  </button>
                )}
              </div>
            </>
          )}

          {/* ── RESULT panel ──────────────────────────────────────────────── */}
          {step === 'result' && plan && (
            <div id="recovery-result" className="recovery-result">
              {/* Header */}
              <div className={`recovery-result-header ${sevCfg.color}`}>
                <div className="recovery-result-sev-row">
                  <sevCfg.icon size={22} />
                  <div>
                    <span className="recovery-sev-label">Exposure Level</span>
                    <strong className="recovery-sev-value">{sevCfg.label}</strong>
                  </div>
                </div>
                <p className="recovery-summary">{plan.summary}</p>
              </div>

              {/* Action sections */}
              <div className="recovery-actions-list">
                {ACTION_SECTIONS.map(({ key, Icon, heading, sub }) => {
                  const actions = plan[key]
                  if (!actions || actions.length === 0) return null
                  const isOpen = !!expandedSections[key]
                  return (
                    <div key={key} className="recovery-action-section">
                      <button
                        className="recovery-action-toggle"
                        onClick={() => toggleSection(key)}
                        aria-expanded={isOpen}
                      >
                        <div className="recovery-action-toggle-left">
                          <span className="recovery-action-icon-wrap">
                            <Icon size={15} />
                          </span>
                          <div>
                            <span className="recovery-action-heading">{heading}</span>
                            <span className="recovery-action-sub">{sub}</span>
                          </div>
                        </div>
                        <div className="recovery-action-meta">
                          <span className="recovery-action-count">{actions.length}</span>
                          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </div>
                      </button>
                      {isOpen && (
                        <ol className="recovery-action-items">
                          {actions.map((action, i) => (
                            <li key={i} className="recovery-action-item">
                              <span className="recovery-action-num">{i + 1}</span>
                              <span>{action}</span>
                            </li>
                          ))}
                        </ol>
                      )}
                    </div>
                  )
                })}
              </div>

              {/* Footer */}
              <div className="recovery-result-footer">
                <p className="recovery-footer-note">
                  These steps are general guidance based on the information you provided.
                  They are not a substitute for professional legal or financial advice.
                  Do not rely on any phone numbers or links except those you independently
                  verify from official sources.
                </p>
                <button className="btn btn-ghost btn-sm" onClick={reset}>
                  ← Update my selections
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </article>
  )
}
