"""The 'Go / No-Go' decision engine."""
from dataclasses import dataclass
import pandas as pd


GO_THRESHOLD_SUN_DEG = 0.0
CAUTION_SUN_DEG = 1.5
STRONG_COMM_WINDOW = 2


@dataclass
class Verdict:
    status: str
    color: str
    label: str
    reasons: list[str]
    score: int


def evaluate_point(row: pd.Series) -> Verdict:
    reasons: list[str] = []
    score = 0

    power_ok = bool(row["power_ok"])
    earth_visible = bool(row["earth_visible"])
    sun_deg = float(row["sun_elevation_deg"])

    if sun_deg > 3.0:
        score += 50
        reasons.append(f"Excellent solar input (Sun at {sun_deg:+.1f} deg)")
    elif sun_deg > CAUTION_SUN_DEG:
        score += 35
        reasons.append(f"Adequate solar input (Sun at {sun_deg:+.1f} deg)")
    elif sun_deg >= GO_THRESHOLD_SUN_DEG:
        score += 20
        reasons.append(f"Marginal solar input (Sun at {sun_deg:+.1f} deg)")
    else:
        reasons.append(f"Sun below horizon ({sun_deg:+.1f} deg) - power unavailable")

    if not power_ok:
        reasons.append("Power system flagged as not-OK for this window")

    if earth_visible:
        score += 50
        reasons.append("Direct-to-Earth line of sight available")
    else:
        reasons.append("Earth occluded by local topography - DTE comms unavailable")

    if power_ok and earth_visible:
        status, color, label = "GO", "#22C55E", "GO - Land"
    elif power_ok and not earth_visible:
        status, color, label = "CAUTION", "#F59E0B", "CAUTION - Power only"
    elif earth_visible and not power_ok:
        status, color, label = "CAUTION", "#F59E0B", "CAUTION - Comms only"
    else:
        status, color, label = "NO-GO", "#EF4444", "NO-GO - Hold"

    return Verdict(status=status, color=color, label=label, reasons=reasons, score=min(score, 100))


def comms_streak(series: pd.DataFrame) -> int:
    best = cur = 0
    for v in series["earth_visible"]:
        if v:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def summary_for_site(series: pd.DataFrame) -> dict:
    total = len(series)
    go_hours = int(((series["power_ok"]) & (series["earth_visible"])).sum())
    power_hours = int(series["power_ok"].sum())
    comms_hours = int(series["earth_visible"].sum())
    return {
        "go_hours": go_hours,
        "total_hours": total,
        "go_pct": round(100 * go_hours / total, 1) if total else 0.0,
        "power_pct": round(100 * power_hours / total, 1) if total else 0.0,
        "comms_pct": round(100 * comms_hours / total, 1) if total else 0.0,
        "comms_streak": comms_streak(series),
    }
