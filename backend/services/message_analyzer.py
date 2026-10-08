import re
from pathlib import Path
import joblib

from .manipulation_analyzer import analyze_manipulation
from .scam_classifier import classify_scam
from .recommendation_engine import recommendations_for
from .risk_engine import combine_risk

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "message_model.joblib"
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)

# ---------------------------------------------------------------------------
# Shortened / suspicious URL patterns
# ---------------------------------------------------------------------------
SHORTENER_DOMAINS = re.compile(
    r"(bit\.ly|tinyurl\.com|goo\.gl|ow\.ly|t\.co|is\.gd|buff\.ly|"
    r"rb\.gy|cutt\.ly|short\.io|tiny\.cc|lc\.cx|clck\.ru|qr\.ae|"
    r"go2l\.ink|x\.co|shorte\.st|adf\.ly|bc\.vc|u\.to|v\.gd)",
    re.I,
)

SUSPICIOUS_URL_RE = re.compile(
    r"https?://(?:[^\s/]*[-.])?(?:"
    # suspicious TLDs commonly used in phishing
    r"[a-z0-9-]+\.(xyz|tk|ml|ga|cf|gq|pw|top|click|link|online|site|info|loan|work|date|racing|review|win|download|stream)/"
    r"|"
    # IP-address hosts
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|"
    # well-known brands embedded in a long non-official domain
    r"(?:gov|bank|sbi|rbi|hdfc|icici|uco|axis|verify|secure|update|login|kyc|account|alert)"
    r"[a-z0-9-]*\.[a-z]{2,10}(?!/)"  # brand keyword + arbitrary domain
    r")",
    re.I,
)

# ---------------------------------------------------------------------------
# Strong positive scam indicators
# ---------------------------------------------------------------------------
STRONG_SCAM_GROUPS = {
    # name: (phrases, base_score_per_hit)
    "Credential request": (
        # "bank details" alone is excluded — it appears in safety advice phrasing.
        # Use explicit request-action forms instead.
        ["otp", "one time password", "security code", "password", "pin", "cvv",
         "login credentials", "enter your otp", "share your otp",
         "enter bank details", "share bank details", "provide bank details",
         "submit bank details", "enter your bank", "give your bank"],
        22,
    ),
    "Payment request": (
        ["pay now", "send money", "transfer money", "upi payment", "upi collect",
         "processing fee", "registration fee", "advance fee", "advance payment",
         "deposit now", "pay immediately", "wire transfer"],
        20,
    ),
    "Prize / lottery claim": (
        ["you won", "you have won", "winner", "lottery", "prize", "cash reward",
         "claim your reward", "free gift", "congratulations you"],
        18,
    ),
    "Threat of blocking / legal": (
        ["account will be blocked", "account suspended", "account will be suspended",
         "legal action will be taken", "arrest warrant", "will be arrested",
         "face penalty", "face legal"],
        18,
    ),
    "Remote access request": (
        ["anydesk", "teamviewer", "remote access", "screen share", "install this app",
         "allow remote"],
        24,
    ),
    "Advance fee": (
        ["advance fee", "advance payment", "registration fee", "processing fee",
         "delivery fee", "custom fee", "customs duty", "release fee"],
        18,
    ),
    "Aggressive urgency + action": (
        # Only scored when COMBINED with another indicator — handled below
        [],
        0,
    ),
}

# ---------------------------------------------------------------------------
# Authority / urgency words — scored LOW on their own; boosted by combination
# ---------------------------------------------------------------------------
AUTHORITY_WORDS = [
    "government", "bank", "police", "rbi", "income tax", "court", "college",
    "university", "company", "support team", "customer care", "official",
    "department", "ministry",
]

URGENCY_WORDS = [
    "urgent", "immediately", "today", "tomorrow", "deadline", "act now",
    "right now", "within 24", "last chance", "hurry", "expire", "expires",
    "asap", "do not delay",
]

# ---------------------------------------------------------------------------
# Safe-context indicators (negative scoring)
# ---------------------------------------------------------------------------
SAFETY_ADVICE_RE = re.compile(
    r"do not share (your )?(otp|password|pin|banking details|bank details|credentials)|"
    r"never share (your )?(otp|password|pin|banking details|bank details)|"
    r"do not give (your )?(otp|password)|"
    r"for your security.{0,30}(do not|never)|"
    r"beware of (fraud|scam|phishing)|"
    r"report (fraud|suspicious)|"
    r"use the official (portal|website|app)",
    re.I,
)

OFFICIAL_PORTAL_RE = re.compile(
    r"official (government |govt |)portal|"
    r"(reschedule|visit|listed) (through|on|at|via) the official|"
    r"official website",
    re.I,
)

APPOINTMENT_RE = re.compile(
    r"\b(appointment|schedule|meeting|interview|session|visit)\b.{0,60}"
    r"\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"\d{1,2}[:h]\d{2}|\d{1,2}\s*(am|pm))\b",
    re.I,
)


def _rule_assessment(text: str):
    """
    Compute a rule-based risk score with:
      - Strong scam indicators (additive)
      - Authority / urgency as low-weight standalone, boosted when combined
      - Suspicious-URL detection
      - Safe-context negative adjustments
    Returns: (score 0-100, signals list, suspicious_phrases list, urls list)
    """
    lower = text.lower()
    score = 0
    signals = []
    suspicious_phrases = []

    urls = URL_RE.findall(text)
    has_url = bool(urls)
    has_suspicious_url = False
    has_shortened_url = False

    if has_url:
        for url in urls:
            if SHORTENER_DOMAINS.search(url):
                has_shortened_url = True
            if SUSPICIOUS_URL_RE.search(url):
                has_suspicious_url = True

    # ── Strong scam indicators ────────────────────────────────────────────
    # Negation patterns: if a credential/payment phrase appears immediately
    # after a "do not" / "never" / "don't" context, don't count it as a hit.
    NEGATION_RE = re.compile(
        r"(do not|don'?t|never|avoid|beware|warn|protect).{0,30}"
        r"(otp|password|pin|cvv|bank details|banking details|credentials|share)",
        re.I,
    )
    negated_zone = set()
    for m in NEGATION_RE.finditer(text):
        negated_zone.add(m.group(2).lower())

    group_hits: dict[str, list[str]] = {}
    for label, (phrases, base) in STRONG_SCAM_GROUPS.items():
        if not phrases:
            continue
        # Exclude phrases whose core keyword appears in negated safety advice
        hits = []
        for p in phrases:
            if p in lower:
                # Check if this phrase is part of a negation context
                core = p.split()[-1]  # e.g. "otp" from "enter your otp"
                if core in negated_zone and label == "Credential request":
                    continue  # skip — it's mentioned in safety advice
                hits.append(p)
        if hits:
            group_hits[label] = hits
            signals.append(label)
            suspicious_phrases.extend(hits)
            increment = min(base + max(0, len(hits) - 1) * 4, 30)
            score += increment

    active_strong = set(group_hits.keys())

    # ── URL analysis ─────────────────────────────────────────────────────
    if has_shortened_url:
        signals.append("Shortened URL detected")
        score += 20
    elif has_suspicious_url:
        signals.append("Suspicious URL detected")
        score += 22
    elif has_url:
        # Plain URL — moderate addition
        signals.append("Contains external link")
        score += 8

    # ── Authority words — very small base, boosted by combination ────────
    authority_hits = [w for w in AUTHORITY_WORDS if w in lower]
    urgency_hits = [w for w in URGENCY_WORDS if w in lower]

    has_authority = bool(authority_hits)
    has_urgency = bool(urgency_hits)

    # Standalone authority: +3
    if has_authority:
        score += 3
        # Don't add to signals unless combined

    # Standalone urgency: +5
    if has_urgency:
        score += 5

    # ── Combination-based boosts ──────────────────────────────────────────
    # Urgency + suspicious URL
    if has_urgency and (has_suspicious_url or has_shortened_url):
        signals.append("Urgency combined with suspicious link")
        score += 20

    # Authority + credential request
    if has_authority and "Credential request" in active_strong:
        signals.append("Authority combined with credential request")
        score += 18

    # Authority + payment request
    if has_authority and "Payment request" in active_strong:
        signals.append("Authority combined with payment request")
        score += 16

    # Authority + urgency + any strong indicator
    if has_authority and has_urgency and active_strong:
        signals.append("Authority + urgency combined with suspicious action")
        score += 14

    # Legal threat + payment (already partially covered above)
    if "Threat of blocking / legal" in active_strong and "Payment request" in active_strong:
        signals.append("Legal threat combined with payment request")
        score += 15

    # Numeric auth code (OTP-style number in message)
    if re.search(r"\b\d{4,6}\b", text) and any(
        k in lower for k in ["otp", "code", "pin"]
    ):
        signals.append("Contains numeric authentication-style code")
        score += 12

    # ── SAFE-CONTEXT NEGATIVE ADJUSTMENTS ────────────────────────────────
    reductions = []

    if not has_url:
        score -= 10
        reductions.append("No URL present (-10)")

    if "Payment request" not in active_strong:
        score -= 10
        reductions.append("No payment request (-10)")

    if "Credential request" not in active_strong:
        score -= 10
        reductions.append("No credential request (-10)")

    # Explicit safety advice ("do not share OTP / password")
    if SAFETY_ADVICE_RE.search(text):
        score -= 15
        reductions.append("Explicit safety advice present (-15)")
        signals.append("Message includes safety/anti-scam advice")

    # Directs user to official portal rather than a link
    if OFFICIAL_PORTAL_RE.search(text) and not has_suspicious_url:
        score -= 8
        reductions.append("Directs to official portal (-8)")

    # Ordinary appointment / schedule info with no suspicious indicators
    if APPOINTMENT_RE.search(text) and not active_strong and not has_url:
        score -= 10
        reductions.append("Ordinary appointment information, no suspicious indicators (-10)")

    if "Prize / lottery claim" not in active_strong:
        score -= 5
        reductions.append("No prize/reward lure (-5)")

    if "Threat of blocking / legal" not in active_strong:
        score -= 5
        reductions.append("No account-blocking threat (-5)")

    # ── Clamp to [0, 100] ────────────────────────────────────────────────
    final = int(round(max(0, min(100, score))))
    return final, list(dict.fromkeys(signals)), list(dict.fromkeys(suspicious_phrases))[:10], urls[:3]


def _ml_probability(text: str):
    if not MODEL_PATH.exists():
        return None
    try:
        model = joblib.load(MODEL_PATH)
        return float(model.predict_proba([text])[0][1])
    except Exception:
        return None


def analyze_message(text: str):
    text = text.strip()
    rule_score, signals, phrases, urls = _rule_assessment(text)
    manipulation = analyze_manipulation(text)
    scam_type, scam_conf, alternative, category_evidence = classify_scam(text, signals)
    ml_p = _ml_probability(text)
    risk = combine_risk(rule_score, ml_p, manipulation["patterns"], scam_conf)

    if risk["risk_score"] <= 35 and not signals:
        scam_type = "No specific scam pattern"
        scam_conf = max(25, min(55, scam_conf))
        alternative = None

    explanation_parts = []
    if signals:
        # Filter out safe-context signals from the warning display
        warning_signals = [s for s in signals if "safety" not in s.lower() and "advice" not in s.lower()]
        if warning_signals:
            explanation_parts.append(
                "Detected warning signs include " + ", ".join(warning_signals[:4]).lower() + "."
            )
    if category_evidence:
        explanation_parts.append(
            "The content matches phrases commonly seen in " + scam_type.lower() + " attempts."
        )
    if not explanation_parts:
        explanation_parts.append(
            "No strong scam pattern was identified from the text alone. "
            "Continue to verify unexpected requests independently."
        )

    return {
        **risk,
        "likely_scam_type": scam_type,
        "confidence": int(round((ml_p * 100 if ml_p is not None else scam_conf))),
        "alternative_possible_type": alternative,
        "detected_signals": signals or ["No strong text-based warning signs detected"],
        "suspicious_phrases": phrases,
        "explanation": " ".join(explanation_parts),
        "manipulation": manipulation,
        "recommended_actions": recommendations_for(scam_type),
        "technical_details": {
            "message_length": len(text),
            "links_found": urls,
            "rule_score": rule_score,
            "ml_probability": ml_p,
            "category_evidence": category_evidence,
        },
    }
