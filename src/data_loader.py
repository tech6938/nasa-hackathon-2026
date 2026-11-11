"""Load and validate the pre-calculated site dataset."""
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sites_data.json"


@st.cache_data(show_spinner=False)
def load_raw_data(path: str | Path = DATA_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_dataframe(path: str | Path = DATA_PATH) -> tuple[pd.DataFrame, list[dict]]:
    raw = load_raw_data(path)
    rows = []
    for site in raw["sites"]:
        for ts in site["timeseries"]:
            rows.append({
                "site_id": site["id"],
                "site_name": site["name"],
                "lat": site["lat"],
                "lon": site["lon"],
                "elevation_m": site["elevation_m"],
                "description": site["description"],
                "risk_notes": site["risk_notes"],
                "timestamp": datetime.fromisoformat(ts["timestamp"].replace("Z", "+00:00")),
                "sun_elevation_deg": ts["sun_elevation_deg"],
                "earth_visible": bool(ts["earth_visible"]),
                "power_ok": bool(ts["power_ok"]),
            })
    df = pd.DataFrame(rows).sort_values(["site_id", "timestamp"]).reset_index(drop=True)
    return df, raw["sites"]


def get_site_series(df: pd.DataFrame, site_id: str) -> pd.DataFrame:
    return (
        df[df["site_id"] == site_id]
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
