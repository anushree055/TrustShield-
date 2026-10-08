"""
TrustShield – Recovery Assistant
=================================
Deterministic, rule-based engine that accepts what the user already did with
suspicious content and returns a structured, prioritised recovery plan.

Functions
---------
assess_recovery_severity(interactions, follow_ups, scam_type, risk_score)
    -> str  ("LOW" | "MODERATE" | "HIGH" | "CRITICAL")

generate_recovery_actions(interactions, follow_ups, scam_type, risk_score)
    -> dict  (structured action plan)

deduplicate_actions(action_list)
    -> list  (unique actions preserving first-seen order)

Public entry point
------------------
build_recovery_plan(interactions, follow_ups, scam_type, risk_score, signals)
    -> dict
"""

from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# Interaction key constants – must match what the frontend sends
# ─────────────────────────────────────────────────────────────────────────────
CLICKED_LINK        = "clicked_link"
ENTERED_CREDENTIALS = "entered_credentials"
SHARED_OTP          = "shared_otp"
SHARED_PIN_CVV      = "shared_pin_cvv"
ENTERED_BANK_UPI    = "entered_bank_upi"
SENT_MONEY          = "sent_money"
DOWNLOADED_FILE     = "downloaded_file"
INSTALLED_APP       = "installed_app"
GAVE_REMOTE_ACCESS  = "gave_remote_access"
SHARED_IDENTITY     = "shared_identity"
REPLIED_ONLY        = "replied_only"
NOT_SURE            = "not_sure"

# Ordered from most to least severe for severity calculation
SEVERITY_RANK = {
    GAVE_REMOTE_ACCESS  : 5,
    SENT_MONEY          : 5,
    SHARED_PIN_CVV      : 4,
    SHARED_OTP          : 3,
    ENTERED_CREDENTIALS : 3,
    ENTERED_BANK_UPI    : 3,
    INSTALLED_APP       : 3,
    DOWNLOADED_FILE     : 2,
    SHARED_IDENTITY     : 2,
    CLICKED_LINK        : 1,
    REPLIED_ONLY        : 1,
    NOT_SURE            : 1,
}

# ─────────────────────────────────────────────────────────────────────────────
# Action catalogue – all possible recovery steps as plain strings
# ─────────────────────────────────────────────────────────────────────────────

# STOP-EXPOSURE actions (always first)
STOP_REMOTE      = "End the active remote-access session immediately if it is still running."
DISCONNECT_NET   = "If a suspicious app is currently active, disconnect from your Wi-Fi or mobile data temporarily to limit its reach."
STOP_REPLY       = "Stop responding to the sender and block the number or account."

# DEVICE actions
UNINSTALL_APP    = "Uninstall the suspicious application from your device."
REVOKE_PERMS     = "Go to Settings → Apps → [app name] → Permissions and revoke all permissions (contacts, SMS, camera, microphone, accessibility, device administrator)."
REMOVE_REMOTE    = "Uninstall any remote-access software (AnyDesk, TeamViewer, QuickSupport, or similar)."
RUN_SCAN         = "Run a reputable antivirus or security scan on your device."
CHECK_DOWNLOADS  = "Check your browser's download folder and delete any file you did not intentionally save."
DONT_OPEN_FILE   = "Do not open the downloaded file. Delete it immediately."
RESTART_DEVICE   = "After completing uninstalls and permission revocations, restart your device."

# ACCOUNT SECURITY actions
CHANGE_PASSWORD  = "Change the exposed password immediately using the official website or app of the affected service — do not use any link from the suspicious message."
CHANGE_ALL_PWD   = "If you use this password on other accounts, change it on all of those accounts too."
ENABLE_2FA       = "Enable two-factor authentication (2FA) on the affected account."
SIGN_OUT         = "Sign out of other active sessions: go to the account's Security or Devices section."
REVIEW_LOGINS    = "Review your login activity and sign-in history for any unrecognised access."
CHANGE_UPI_PIN   = "Change your UPI PIN from inside your UPI app (not via any external link)."
BLOCK_CARD       = "Contact your bank or use their official app to lock or freeze the affected card immediately."
CANCEL_MANDATES  = "Review and cancel any unknown UPI autopay mandates or standing instructions in your UPI or banking app."
CONTACT_BANK     = "Contact your bank directly using the number printed on your card or the official website — not via any link in the suspicious message."
CONTACT_BANK_OTP = "Contact the bank or service provider whose OTP was shared, using their official customer-care channel."
CHANGE_CARD_PIN  = "Ask your bank to reset your card PIN or issue a replacement card if recommended by the bank."
SECURE_EMAIL     = "Check and secure your primary email account, as it is often used for password recovery on other services."

# FINANCIAL PROTECTION actions
FREEZE_CARD      = "Ask your card issuer to freeze or block the compromised card and request a replacement."
SAVE_TXNID       = "Save all transaction IDs, screenshots, bank references, and chat evidence before they are lost."
CONTACT_PAYMENT  = "Contact your payment provider (bank, UPI app, or wallet) immediately and report the suspicious transaction."
NO_MORE_MONEY    = "Do not send additional money even if the sender promises a refund or claims it is required to recover your earlier payment."
MONITOR_TXNS     = "Monitor your bank and UPI statements closely over the next several weeks for any unauthorised activity."

# IDENTITY PROTECTION actions
WATCH_MISUSE     = "Monitor for signs of identity misuse: unexpected loan notices, new accounts opened in your name, or unusual credit enquiries."
STOP_SHARING     = "Stop sharing any further personal documents or details with this sender."
PRESERVE_EVIDENCE = "Take screenshots of all communication, URLs visited, and transaction records and store them safely."
CHANGE_CREDS_OTHER = "If account credentials were also shared, change passwords from a trusted device that is different from the one used during the incident."

# REPORTING actions
REPORT_CYBERCRIME = "Report the incident through your country's official cybercrime reporting channel. In India, use cybercrime.gov.in or call 1930."
REPORT_BANK      = "Inform your bank's fraud team about the incident, providing all available evidence."
REPORT_UPI       = "Report the fraudulent transaction in your UPI app under 'Report fraud' or 'Raise dispute'."
BLOCK_SENDER     = "Block and report the sender's number or account on the platform used."

# MONITORING actions
WATCH_RESETS     = "Watch for unsolicited password-reset emails or SMS messages you did not request."
WATCH_NEW_LOGINS = "Monitor your email for alerts about new sign-ins from unrecognised devices or locations."
WATCH_ACCOUNTS   = "Periodically review your bank, UPI, and linked payment accounts for any unfamiliar charges."
NO_MORE_OTP      = "Never share an OTP, PIN, or password with anyone — even someone claiming to be from your bank, government, or technical support."
FOLLOW_UP_SCAM   = "Be cautious of follow-up contact that may offer to 'recover' your money or 'fix' the problem — this is often a second scam targeting the same victim."

# BROWSER / LINK actions
CLOSE_TAB        = "Close the suspicious page or tab. Do not return to it."
CLEAR_DOWNLOADS  = "Check your browser's download history and remove anything that started automatically."
CHECK_NOTIFS     = "Review browser notification permissions (Settings → Site settings → Notifications) and revoke any unknown entries."
SAFE_BROWSING    = "Continue monitoring your account activity if the link was related to banking or payments — a click alone does not guarantee credential theft, but caution is warranted."

# NOT-SURE conservative set
CHANGE_IMPORTANT = "As a precaution, change passwords for your most important accounts (email, banking, UPI) from a trusted device."
CHECK_BANK_APP   = "Open your banking and UPI apps directly and review recent transactions."
CHECK_DEVICE_APP = "Check your installed apps for anything you do not recognise and uninstall unknown applications."

# ─────────────────────────────────────────────────────────────────────────────
# SEVERITY LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def assess_recovery_severity(
    interactions: List[str],
    follow_ups: Dict[str, Any],
    scam_type: str,
    risk_score: int,
) -> str:
    """
    Return a recovery severity level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL".

    Severity is driven by the WORST single action the user took, then lifted
    further by combinations and the original risk score.
    """
    if not interactions:
        return "LOW"

    max_rank = max((SEVERITY_RANK.get(i, 1) for i in interactions), default=1)

    # Rank → base severity
    if max_rank >= 5:
        severity = "CRITICAL"
    elif max_rank == 4:
        severity = "CRITICAL"
    elif max_rank == 3:
        severity = "HIGH"
    elif max_rank == 2:
        severity = "MODERATE"
    else:
        severity = "LOW"

    # Combinations that escalate severity
    iset = set(interactions)
    if ENTERED_CREDENTIALS in iset and SHARED_OTP in iset:
        severity = "HIGH"  # already HIGH, but ensure it
    if SENT_MONEY in iset and (GAVE_REMOTE_ACCESS in iset or INSTALLED_APP in iset):
        severity = "CRITICAL"
    if INSTALLED_APP in iset and SHARED_OTP in iset:
        severity = _escalate(severity, "HIGH")

    # Risk score can nudge up only when borderline
    if risk_score >= 75 and severity == "MODERATE":
        severity = "HIGH"

    # Clicking link only → cap at MODERATE (never automatically HIGH)
    if iset == {CLICKED_LINK} or iset == {CLICKED_LINK, NOT_SURE}:
        severity = "LOW" if risk_score < 60 else "MODERATE"

    # Replied only → LOW always
    if iset == {REPLIED_ONLY} or iset == {REPLIED_ONLY, NOT_SURE}:
        severity = "LOW"

    return severity


def _escalate(current: str, to: str) -> str:
    """Return the higher of two severity levels."""
    order = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    return to if order.index(to) > order.index(current) else current


# ─────────────────────────────────────────────────────────────────────────────
# ACTION GENERATION LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def generate_recovery_actions(
    interactions: List[str],
    follow_ups: Dict[str, Any],
    scam_type: str,
    risk_score: int,
) -> Dict[str, List[str]]:
    """
    Return a dict with categorised action lists.  Every list is independently
    deduplicated; duplicates across categories are allowed because each category
    is shown in its own section.
    """
    iset = set(interactions)
    if not iset:
        return {}

    immediate: List[str]       = []
    account_security: List[str] = []
    financial: List[str]        = []
    device: List[str]           = []
    identity: List[str]         = []
    reporting: List[str]        = []
    monitoring: List[str]       = []

    # ── A. GAVE REMOTE ACCESS (critical – stop first) ────────────────────────
    if GAVE_REMOTE_ACCESS in iset:
        immediate += [STOP_REMOTE, DISCONNECT_NET]
        device    += [REMOVE_REMOTE, REVOKE_PERMS, RUN_SCAN, RESTART_DEVICE]
        account_security += [CHANGE_CREDS_OTHER, SECURE_EMAIL]
        financial += [CONTACT_BANK, MONITOR_TXNS]
        reporting += [REPORT_CYBERCRIME]
        monitoring += [WATCH_ACCOUNTS, FOLLOW_UP_SCAM]

    # ── B. SENT MONEY (critical financial) ───────────────────────────────────
    if SENT_MONEY in iset:
        immediate += [SAVE_TXNID, CONTACT_PAYMENT]
        financial += [CONTACT_BANK, NO_MORE_MONEY, MONITOR_TXNS]
        reporting += [REPORT_CYBERCRIME, REPORT_BANK]
        # Follow-up: how was payment made?
        payment_method = follow_ups.get("payment_method", "")
        if payment_method == "upi":
            financial += [REPORT_UPI, CANCEL_MANDATES]
        elif payment_method in ("debit_card", "credit_card"):
            financial += [FREEZE_CARD, CHANGE_CARD_PIN]
        monitoring += [WATCH_ACCOUNTS, FOLLOW_UP_SCAM]

    # ── C. SHARED PIN / CVV / CARD DETAILS (critical) ────────────────────────
    if SHARED_PIN_CVV in iset:
        immediate += [CONTACT_BANK]
        financial += [FREEZE_CARD, CHANGE_CARD_PIN, MONITOR_TXNS]
        account_security += [BLOCK_CARD]
        monitoring += [WATCH_ACCOUNTS]

    # ── D. SHARED OTP (high) ─────────────────────────────────────────────────
    if SHARED_OTP in iset:
        immediate += [STOP_REPLY, CONTACT_BANK_OTP]
        account_security += [REVIEW_LOGINS, ENABLE_2FA]
        monitoring += [NO_MORE_OTP, WATCH_ACCOUNTS, WATCH_RESETS]
        # Follow-up: which service OTP?
        otp_service = follow_ups.get("otp_service", "")
        if otp_service in ("banking", "upi"):
            financial += [CONTACT_BANK, CANCEL_MANDATES, MONITOR_TXNS]
        elif otp_service == "login":
            account_security += [CHANGE_PASSWORD, SIGN_OUT]

    # ── E. ENTERED CREDENTIALS (password / username) (high) ──────────────────
    if ENTERED_CREDENTIALS in iset:
        immediate += [CHANGE_PASSWORD]
        account_security += [ENABLE_2FA, SIGN_OUT, REVIEW_LOGINS, SECURE_EMAIL]
        monitoring += [WATCH_RESETS, WATCH_NEW_LOGINS]
        # Follow-up: was password reused?
        pwd_reused = follow_ups.get("password_reused", "")
        if pwd_reused in ("yes", "not_sure"):
            account_security += [CHANGE_ALL_PWD]
        # Escalate if banking-related scam
        if scam_type in ("Banking Phishing", "Credential Theft", "OTP Scam"):
            financial += [CONTACT_BANK, MONITOR_TXNS]

    # ── F. ENTERED BANK / UPI DETAILS (high) ─────────────────────────────────
    if ENTERED_BANK_UPI in iset:
        immediate += [CONTACT_BANK]
        account_security += [CHANGE_UPI_PIN]
        financial += [CANCEL_MANDATES, MONITOR_TXNS]
        reporting += [REPORT_BANK]
        monitoring += [WATCH_ACCOUNTS, NO_MORE_OTP]

    # ── G. INSTALLED APP (high) ───────────────────────────────────────────────
    if INSTALLED_APP in iset:
        immediate += [DISCONNECT_NET]
        device    += [UNINSTALL_APP, REVOKE_PERMS, RUN_SCAN, RESTART_DEVICE]
        account_security += [CHANGE_CREDS_OTHER, SECURE_EMAIL]
        monitoring += [WATCH_NEW_LOGINS, FOLLOW_UP_SCAM]
        # Follow-up: what kind of app?
        app_type = follow_ups.get("app_type", "")
        if app_type in ("remote_access", "unknown"):
            immediate += [STOP_REMOTE]
            device    += [REMOVE_REMOTE]

    # ── H. DOWNLOADED FILE (moderate) ────────────────────────────────────────
    if DOWNLOADED_FILE in iset:
        immediate += [DONT_OPEN_FILE]
        device    += [CHECK_DOWNLOADS, RUN_SCAN]
        monitoring += [WATCH_NEW_LOGINS]

    # ── I. CLICKED LINK (low / moderate) ─────────────────────────────────────
    if CLICKED_LINK in iset:
        immediate += [CLOSE_TAB]
        device    += [CLEAR_DOWNLOADS, CHECK_NOTIFS]
        # Follow-up: did you enter anything after clicking?
        entered_after = follow_ups.get("entered_after_click", "")
        if entered_after == "yes":
            # Escalate: treat as credential entry at minimum
            account_security += [CHANGE_PASSWORD, REVIEW_LOGINS]
            monitoring += [WATCH_RESETS]
        elif entered_after == "not_sure":
            monitoring += [WATCH_ACCOUNTS, SAFE_BROWSING]
        else:
            monitoring += [SAFE_BROWSING]

    # ── J. SHARED IDENTITY INFORMATION ───────────────────────────────────────
    if SHARED_IDENTITY in iset:
        immediate += [STOP_SHARING, PRESERVE_EVIDENCE]
        identity  += [WATCH_MISUSE, FOLLOW_UP_SCAM]
        monitoring += [WATCH_ACCOUNTS]
        # If credentials also compromised
        if ENTERED_CREDENTIALS in iset or SHARED_OTP in iset:
            identity += [CHANGE_CREDS_OTHER]

    # ── K. REPLIED ONLY ───────────────────────────────────────────────────────
    if REPLIED_ONLY in iset and len(iset) == 1:
        immediate += [STOP_REPLY, BLOCK_SENDER]
        monitoring += [FOLLOW_UP_SCAM]

    # ── L. NOT SURE ───────────────────────────────────────────────────────────
    if NOT_SURE in iset and len(iset) == 1:
        immediate    += [STOP_REPLY]
        account_security += [CHANGE_IMPORTANT]
        financial    += [CHECK_BANK_APP]
        device       += [CHECK_DEVICE_APP, RUN_SCAN]
        monitoring   += [WATCH_ACCOUNTS, FOLLOW_UP_SCAM]

    # ── Always-add reporting / block sender nudge ────────────────────────────
    if REPORT_CYBERCRIME not in reporting and any(
        i in iset for i in [SENT_MONEY, SHARED_PIN_CVV, GAVE_REMOTE_ACCESS, ENTERED_BANK_UPI]
    ):
        reporting += [REPORT_CYBERCRIME]
    if BLOCK_SENDER not in immediate and STOP_REPLY not in immediate and REPLIED_ONLY not in iset:
        reporting += [BLOCK_SENDER]

    return {
        "immediate_actions"  : deduplicate_actions(immediate),
        "account_security"   : deduplicate_actions(account_security),
        "financial_actions"  : deduplicate_actions(financial),
        "device_actions"     : deduplicate_actions(device),
        "identity_actions"   : deduplicate_actions(identity),
        "reporting_actions"  : deduplicate_actions(reporting),
        "monitoring_actions" : deduplicate_actions(monitoring),
    }


def deduplicate_actions(action_list: List[str]) -> List[str]:
    """Remove duplicates from a list while preserving insertion order."""
    seen = set()
    out = []
    for item in action_list:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

_SUMMARY_TEMPLATES: Dict[frozenset, str] = {
    frozenset({GAVE_REMOTE_ACCESS, SENT_MONEY}):
        "You gave remote control of your device and sent money. This is a critical situation — act on the steps below immediately.",
    frozenset({SENT_MONEY}):
        "You approved or sent a payment to the suspicious contact. Contact your payment provider right away.",
    frozenset({SHARED_PIN_CVV}):
        "You shared card details that could allow unauthorised transactions. Contact your bank immediately.",
    frozenset({SHARED_OTP, ENTERED_CREDENTIALS}):
        "You shared your credentials and an OTP. Your account may be at immediate risk — act on the steps below without delay.",
    frozenset({SHARED_OTP}):
        "You shared an OTP. Contact the relevant service through its official channel and review recent account activity.",
    frozenset({ENTERED_CREDENTIALS}):
        "You entered your login credentials on a page TrustShield flagged as suspicious. Your credentials may have been exposed.",
    frozenset({ENTERED_BANK_UPI}):
        "You entered banking or UPI details. Review your transactions and contact your bank if anything seems unusual.",
    frozenset({GAVE_REMOTE_ACCESS}):
        "You gave remote access to your device. End the session immediately and follow the device-security steps below.",
    frozenset({INSTALLED_APP}):
        "You installed an application from an untrusted source. This can increase device-security risk — follow the steps below.",
    frozenset({DOWNLOADED_FILE}):
        "You downloaded a file from a suspicious source. Do not open it, and run a security scan.",
    frozenset({CLICKED_LINK}):
        "You clicked the suspicious link. If you did not enter any information, the risk is likely low — but review the steps below as a precaution.",
    frozenset({SHARED_IDENTITY}):
        "You shared personal identity information. Monitor for any signs of misuse and preserve the evidence.",
    frozenset({REPLIED_ONLY}):
        "You replied to the suspicious sender. Stop further communication and block the contact.",
    frozenset({NOT_SURE}):
        "You're not sure what happened. Follow the conservative checklist below as a precaution.",
}


def _build_summary(interactions: List[str], severity: str) -> str:
    """
    Return a plain-language summary sentence.  Exact-match first; fallback
    to the worst single interaction.
    """
    iset = frozenset(interactions)
    # Exact match
    if iset in _SUMMARY_TEMPLATES:
        return _SUMMARY_TEMPLATES[iset]
    # Find worst single key in the set
    worst = max(interactions, key=lambda k: SEVERITY_RANK.get(k, 0))
    single = frozenset({worst})
    if single in _SUMMARY_TEMPLATES:
        base = _SUMMARY_TEMPLATES[single]
        n = len(interactions)
        if n > 1:
            return base + f" You also selected {n - 1} additional action(s) — all relevant steps are included below."
        return base
    return "You interacted with suspicious content. Review and follow the personalised steps below."


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def build_recovery_plan(
    interactions: List[str],
    follow_ups: Dict[str, Any],
    scam_type: str,
    risk_score: int,
    signals: List[str],
) -> Dict:
    """
    Build and return the complete recovery plan.

    Parameters
    ----------
    interactions : list[str]
        Interaction keys selected by the user (see constants above).
    follow_ups   : dict
        Answers to optional follow-up questions keyed by question ID.
    scam_type    : str
        The likely_scam_type from the analysis result.
    risk_score   : int
        The original risk_score (0-100) from the analysis result.
    signals      : list[str]
        The detected_signals from the analysis result.

    Returns
    -------
    dict
        {
          "severity"          : "LOW"|"MODERATE"|"HIGH"|"CRITICAL",
          "summary"           : str,
          "immediate_actions" : [str, ...],
          "account_security"  : [str, ...],
          "financial_actions" : [str, ...],
          "device_actions"    : [str, ...],
          "identity_actions"  : [str, ...],
          "reporting_actions" : [str, ...],
          "monitoring_actions": [str, ...],
        }
    """
    # Normalise: remove duplicates, keep only valid keys
    valid_keys = set(SEVERITY_RANK.keys())
    clean = list(dict.fromkeys(i for i in interactions if i in valid_keys))

    if not clean:
        return {
            "severity": "LOW",
            "summary": "No interactions were selected. If you are unsure, follow the general safety checklist from the main result panel.",
            "immediate_actions": [],
            "account_security": [],
            "financial_actions": [],
            "device_actions": [],
            "identity_actions": [],
            "reporting_actions": [],
            "monitoring_actions": [],
        }

    severity = assess_recovery_severity(clean, follow_ups, scam_type, risk_score)
    actions  = generate_recovery_actions(clean, follow_ups, scam_type, risk_score)
    summary  = _build_summary(clean, severity)

    return {
        "severity"          : severity,
        "summary"           : summary,
        **actions,
    }
