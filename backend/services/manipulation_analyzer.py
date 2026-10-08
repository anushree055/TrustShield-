import re
from typing import Dict, List

PATTERNS = {
    "urgency": {
        "label": "Urgency",
        "keywords": ["urgent", "immediately", "act now", "right now", "today only", "within", "last chance", "hurry", "expire", "expires", "asap"],
        "explanation": "Pressures you to act quickly before you have time to verify the request."
    },
    "fear": {
        "label": "Fear",
        "keywords": ["blocked", "suspended", "legal action", "penalty", "arrest", "terminated", "frozen", "unauthorized", "fraud detected", "deactivated"],
        "explanation": "Uses threats or alarming consequences to push you into reacting emotionally."
    },
    "authority": {
        "label": "Authority",
        "keywords": ["bank", "government", "police", "income tax", "customer care", "support team", "official", "rbi", "kyc", "manager", "department"],
        "explanation": "Claims or implies authority to make the request feel trustworthy."
    },
    "reward": {
        "label": "Reward",
        "keywords": ["you won", "winner", "prize", "cashback", "free gift", "reward", "lottery", "bonus", "congratulations", "guaranteed return"],
        "explanation": "Uses an attractive reward or gain to reduce caution."
    },
    "scarcity": {
        "label": "Scarcity",
        "keywords": ["limited time", "last chance", "only today", "few left", "expires soon", "limited slots", "offer ends"],
        "explanation": "Creates artificial scarcity so you feel you may miss an opportunity."
    },
    "trust": {
        "label": "Trust Exploitation",
        "keywords": ["dear customer", "valued customer", "trusted", "verified", "official account", "friend", "family", "known contact"],
        "explanation": "Uses familiar or reassuring language to lower your guard."
    },
    "financial_pressure": {
        "label": "Financial Pressure",
        "keywords": ["pay now", "payment", "transfer", "deposit", "processing fee", "registration fee", "upi", "send money", "refund fee", "advance payment"],
        "explanation": "Pushes you to send money or approve a payment quickly."
    },
    "credential_pressure": {
        "label": "Credential Pressure",
        "keywords": ["otp", "password", "pin", "cvv", "login", "verify account", "credentials", "security code", "bank details", "aadhaar", "pan number"],
        "explanation": "Attempts to obtain sensitive account or identity information."
    },
}

def analyze_manipulation(text: str) -> Dict:
    lower = text.lower()
    results = []
    for key, spec in PATTERNS.items():
        matches: List[str] = []
        for kw in spec["keywords"]:
            if kw in lower:
                matches.append(kw)
        # Deterministic and explainable score: 0, then rises with distinct matches.
        score = min(100, len(matches) * 24 + (10 if len(matches) >= 2 else 0))
        results.append({
            "key": key,
            "label": spec["label"],
            "score": score,
            "matches": matches[:5],
            "explanation": spec["explanation"],
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    dominant = [r["label"] for r in results if r["score"] >= 35][:2]
    return {
        "patterns": results,
        "dominant_strategy": " + ".join(dominant) if dominant else "No strong manipulation pattern detected"
    }
