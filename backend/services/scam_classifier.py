from typing import Tuple, List

# ---------------------------------------------------------------------------
# Category rules: each entry is (category_name, keywords, weight)
# Weight > 1 means the keyword is a stronger indicator.
# ---------------------------------------------------------------------------
CATEGORY_RULES = [
    ("OTP Scam",
     ["otp", "one time password", "enter your otp", "share otp", "share your otp", "verification code", "security code"],
     1.5),
    ("Fake Job Scam",
     ["job offer", "hiring", "work from home", "registration fee", "interview fee", "salary advance", "recruiter"],
     1.2),
    ("Lottery / Prize Scam",
     ["lottery", "you won", "you have won", "winner", "prize", "cash reward", "claim reward", "claim your prize"],
     1.4),
    ("Investment Scam",
     ["guaranteed return", "double your money", "crypto profit", "trading signal", "high return", "investment profit"],
     1.3),
    ("Delivery Scam",
     ["parcel", "courier", "shipping fee", "package held", "customs fee", "delivery fee"],
     1.1),
    ("UPI / Payment Scam",
     ["upi collect", "qr code payment", "pay now", "send money", "transfer money", "upi payment request", "advance fee"],
     1.3),
    ("Fake Shopping Scam",
     ["order now", "limited stock", "cash on delivery fraud", "seller scam"],
     1.0),
    ("Tech Support Scam",
     ["remote access", "anydesk", "teamviewer", "virus detected", "technical support scam", "computer infected"],
     1.5),
    ("Impersonation Scam",
     ["i am your", "new number", "urgent transfer", "boss request", "ceo fraud"],
     1.3),
    ("Banking Phishing",
     ["account blocked", "account suspended", "netbanking", "debit card blocked",
      "credit card blocked", "kyc update required", "kyc expired"],
     1.4),
    ("Credential Theft",
     ["password", "enter your password", "pin", "cvv", "login credentials", "verify account", "bank details"],
     1.4),
    # "bank" alone is NOT included here — it must be combined with a blocking phrase
    # "government" alone is NOT included — it is an authority word, not a scam keyword
]

# ---------------------------------------------------------------------------
# Keywords that should reduce scam confidence when present
# (typical in legitimate official communications)
# ---------------------------------------------------------------------------
SAFE_CONTEXT_KEYWORDS = [
    "do not share",
    "never share",
    "do not give",
    "for your security",
    "official portal",
    "official website",
    "official government portal",
    "reschedule",
    "bring your original",
    "appointment",
    "arrive early",
    "supporting documents",
    "application receipt",
]


def classify_scam(
    text: str, detected_signals: List[str] | None = None
) -> Tuple[str, int, str | None, List[str]]:
    lower = text.lower()
    scored = []

    for category, keywords, weight in CATEGORY_RULES:
        matches = [kw for kw in keywords if kw in lower]
        if matches:
            weighted_score = len(matches) * weight
            scored.append((weighted_score, category, matches))

    if not scored:
        # No keyword hits at all — check if detected_signals hint at a category
        if detected_signals and any("credential" in s.lower() for s in detected_signals):
            return "Credential Theft", 48, None, []
        if detected_signals and any("payment" in s.lower() for s in detected_signals):
            return "UPI / Payment Scam", 48, None, []
        return "Generic Suspicious Content", 30, None, []

    scored.sort(reverse=True)
    top_weighted, top_category, matches = scored[0]
    alternative = scored[1][1] if len(scored) > 1 and scored[1][0] > 0 else None

    # Base confidence from keyword matches
    raw_match_count = len(matches)
    confidence = min(96, 50 + int(top_weighted * 9) + (5 if raw_match_count >= 2 else 0))

    # Reduce confidence when safe-context keywords are present
    safe_hits = [kw for kw in SAFE_CONTEXT_KEYWORDS if kw in lower]
    if safe_hits:
        # Each safe keyword reduces confidence by 6, capped at -25 total
        reduction = min(25, len(safe_hits) * 6)
        confidence = max(20, confidence - reduction)

    return top_category, confidence, alternative, matches[:5]
