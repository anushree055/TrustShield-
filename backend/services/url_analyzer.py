import ipaddress
import re
from urllib.parse import urlparse
from pathlib import Path
import joblib

from .risk_engine import combine_risk
from .recommendation_engine import recommendations_for

SUSPICIOUS_WORDS = ["login", "verify", "secure", "update", "account", "bank", "banking", "password", "confirm", "wallet", "payment", "signin", "kyc", "otp", "bonus", "prize"]
SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "tiny.cc"]
SUSPICIOUS_EXTENSIONS = [".exe", ".scr", ".zip", ".apk", ".js"]
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "url_model.joblib"

def _ensure_scheme(url: str) -> str:
    if not re.match(r"^https?://", url, re.I):
        return "http://" + url
    return url

def extract_features(url: str):
    prepared = _ensure_scheme(url.strip())
    parsed = urlparse(prepared)
    host = parsed.hostname or ""
    path = parsed.path or ""
    try:
        ipaddress.ip_address(host)
        has_ip = 1
    except Exception:
        has_ip = 0
    features = {
        "url_length": len(prepared),
        "dot_count": prepared.count("."),
        "hyphen_count": prepared.count("-"),
        "special_count": len(re.findall(r"[^A-Za-z0-9]", prepared)),
        "has_at": int("@" in prepared),
        "has_ip": has_ip,
        "uses_https": int(parsed.scheme.lower() == "https"),
        "subdomain_count": max(0, host.count(".") - 1),
        "suspicious_word_count": sum(1 for w in SUSPICIOUS_WORDS if w in prepared.lower()),
        "is_shortener": int(any(s in host.lower() for s in SHORTENERS)),
        "digit_count": sum(ch.isdigit() for ch in host),
        "suspicious_extension": int(any(path.lower().endswith(ext) for ext in SUSPICIOUS_EXTENSIONS)),
    }
    return prepared, host, features

def _rule_assessment(url: str, host: str, f: dict):
    signals = []
    score = 0
    if f["url_length"] > 75:
        score += 12; signals.append("Unusually long URL")
    if f["has_ip"]:
        score += 24; signals.append("Uses an IP address instead of a normal domain")
    if not f["uses_https"]:
        score += 10; signals.append("Uses HTTP instead of HTTPS")
    if f["has_at"]:
        score += 18; signals.append("Contains @ symbol, which can obscure the real destination")
    if f["hyphen_count"] >= 3:
        score += 9; signals.append("Contains many hyphens")
    if f["subdomain_count"] >= 3:
        score += 14; signals.append("Contains many subdomains")
    if f["suspicious_word_count"]:
        pts = min(24, f["suspicious_word_count"] * 6)
        score += pts; signals.append("Contains security/account-related bait words")
    if f["is_shortener"]:
        score += 18; signals.append("Uses a URL shortening service")
    if f["digit_count"] >= 6:
        score += 8; signals.append("Domain contains many digits")
    if f["suspicious_extension"]:
        score += 20; signals.append("Links directly to a potentially risky file type")
    if host.startswith("xn--"):
        score += 20; signals.append("Uses punycode in the domain")
    return min(100, score), signals

def _ml_probability(features: dict):
    if not MODEL_PATH.exists():
        return None
    try:
        model = joblib.load(MODEL_PATH)
        cols = ["url_length","dot_count","hyphen_count","special_count","has_at","has_ip","uses_https","subdomain_count","suspicious_word_count","is_shortener","digit_count","suspicious_extension"]
        row = [[features[c] for c in cols]]
        return float(model.predict_proba(row)[0][1])
    except Exception:
        return None

def analyze_url(url: str):
    prepared, host, features = extract_features(url)
    rule_score, signals = _rule_assessment(prepared, host, features)
    lower = prepared.lower()
    if "bank" in lower or "kyc" in lower:
        scam_type = "Banking Phishing"
        confidence = 72 + min(20, features["suspicious_word_count"] * 4)
    elif any(x in lower for x in ["login", "password", "signin", "verify"]):
        scam_type = "Credential Theft"
        confidence = 70 + min(20, features["suspicious_word_count"] * 4)
    elif any(x in lower for x in ["shop", "deal", "discount", "offer"]):
        scam_type = "Fake Shopping Scam"
        confidence = 66
    else:
        scam_type = "Generic Suspicious Content" if rule_score >= 35 else "No specific scam pattern"
        confidence = 58 if rule_score >= 35 else 35
    ml_p = _ml_probability(features)
    # URL manipulation uses a neutral placeholder because psychology is mainly text-based.
    patterns = [{"label":"URL Threat Pressure","score":min(100,features["suspicious_word_count"]*22),"matches":[],"explanation":"Risk-related bait words inside the URL can pressure users to trust a fake destination."}]
    risk = combine_risk(rule_score, ml_p, patterns, confidence)
    explanation = (
        f"TrustShield found {len(signals)} suspicious URL signal(s). "
        + ("The link has characteristics commonly associated with phishing or deceptive destinations." if signals else "The URL has few obvious structural warning signs, but a low score does not guarantee safety.")
    )
    return {
        **risk,
        "likely_scam_type": scam_type,
        "confidence": min(96, int(round((ml_p*100 if ml_p is not None else confidence)))),
        "alternative_possible_type": "Credential Theft" if scam_type == "Banking Phishing" else None,
        "detected_signals": signals or ["No strong structural warning signs detected"],
        "suspicious_phrases": [w for w in SUSPICIOUS_WORDS if w in lower][:6],
        "explanation": explanation,
        "manipulation": {"patterns": patterns, "dominant_strategy": patterns[0]["label"] if patterns[0]["score"] >= 35 else "No strong manipulation pattern detected"},
        "recommended_actions": recommendations_for(scam_type),
        "technical_details": {"normalized_url": prepared, "host": host, "features": features, "ml_probability": ml_p},
    }
