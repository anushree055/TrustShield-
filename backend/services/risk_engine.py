from typing import Dict, List


def level_for(score: int) -> str:
    if score <= 20:
        return "Very Low Risk"
    if score <= 40:
        return "Low Risk"
    if score <= 60:
        return "Moderate Risk"
    if score <= 80:
        return "High Risk"
    return "Very High Risk"


def combine_risk(
    rule_score: float,
    ml_probability: float | None,
    manipulation_patterns: List[Dict],
    scam_confidence: int,
) -> Dict:
    """
    Combine signals into a final risk score.

    Weighting rationale
    -------------------
    rule_score      – now encodes safe-context adjustments (negative scoring),
                      so it is the most reliable signal.  Weight: 0.40
    ml_probability  – trained classifier; may not reflect safe-context edits.
                      Weight: 0.30
    manipulation    – pattern-level manipulation signals.  Weight: 0.18
    scam_confidence – keyword category confidence; also adjusted for safe
                      context in scam_classifier.  Weight: 0.12

    The authority/urgency patterns in manipulation_analyzer fire on words like
    "government" and "tomorrow".  To prevent them from inflating the final
    score for legitimate messages, we cap the manipulation contribution at the
    rule_score normalised value when rule_score is low.
    """
    rule_norm = max(0.0, min(1.0, rule_score / 100.0))
    scam_norm = max(0.0, min(1.0, scam_confidence / 100.0))
    ml_norm = ml_probability if ml_probability is not None else rule_norm

    # Cap manipulation influence: when rule_score is low (≤ 25), the
    # manipulation contribution cannot exceed rule_norm.  This prevents
    # innocuous authority/urgency words from pushing the combined score high.
    raw_manipulation = max([p["score"] for p in manipulation_patterns] + [0]) / 100.0
    manipulation = min(raw_manipulation, max(rule_norm, 0.25)) if rule_norm <= 0.25 else raw_manipulation

    weighted = (
        rule_norm      * 0.40 +
        ml_norm        * 0.30 +
        manipulation   * 0.18 +
        scam_norm      * 0.12
    )

    score = int(round(max(0, min(1, weighted)) * 100))

    contributors = [
        {"label": "Threat indicators (rule-based)", "points": int(round(rule_norm * 40))},
        {"label": "ML / classifier signal",         "points": int(round(ml_norm * 30))},
        {"label": "Manipulation patterns",           "points": int(round(manipulation * 18))},
        {"label": "Scam pattern confidence",         "points": int(round(scam_norm * 12))},
    ]

    return {
        "risk_score": score,
        "risk_level": level_for(score),
        "score_contributors": contributors,
    }
