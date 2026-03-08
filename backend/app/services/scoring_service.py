"""Composite score calculation and risk band mapping."""

DIMENSION_WEIGHTS = {
    "cybersecurity": 0.20,
    "regulatory": 0.18,
    "operational": 0.15,
    "news_legal": 0.12,
    "financial_health": 0.12,
    "data_privacy": 0.08,
    "concentration": 0.07,
    "esg": 0.04,
    "fourth_party": 0.04,
}


def compute_composite_score(
    cybersecurity: int,
    regulatory: int,
    operational: int,
    news_legal: int,
    financial_health: int,
    data_privacy: int,
    concentration: int,
    esg: int,
    fourth_party: int,
) -> int:
    scores = {
        "cybersecurity": cybersecurity,
        "regulatory": regulatory,
        "operational": operational,
        "news_legal": news_legal,
        "financial_health": financial_health,
        "data_privacy": data_privacy,
        "concentration": concentration,
        "esg": esg,
        "fourth_party": fourth_party,
    }
    total = sum(scores[dim] * weight for dim, weight in DIMENSION_WEIGHTS.items())
    return int(round(total))


def compute_risk_band(score: int) -> str:
    if score <= 24:
        return "critical"
    if score <= 49:
        return "high"
    if score <= 74:
        return "watch"
    return "stable"
