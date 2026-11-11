"""
Lunar Landing Site Navigator - NASA Space Apps Challenge
Go / No-Go Risk Dashboard.

Run with:  streamlit run app.py
"""
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(
    page_title="Lunar Landing Site Navigator",
    page_icon="🌕",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_loader import load_dataframe, get_site_series
from src.logic import evaluate_point, summary_for_site
from src.charts import (
    sun_elevation_chart,
    comms_window_chart,
    timeline_status_chart,
    site_map_chart,
)

css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


st.markdown(
    """
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:4px;">
        <div style="font-size:38px;">🌕</div>
        <div>
            <h1 style="margin:0; padding:0;">Lunar Landing Site Navigator</h1>
            <p style="margin:0; color:#94A3B8;">
                Go / No-Go risk dashboard for Artemis south-pole candidates -
                power availability vs. direct-to-Earth comms.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()


try:
    df, sites_meta = load_dataframe()
except Exception as e:
    st.error(f"Failed to load site data: {e}")
    st.stop()


with st.sidebar:
    st.header("🛠️ Mission Parameters")
    
    # --- NEW: CALENDAR DATE PICKER ---
    # Find the min and max dates from our JSON data
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()
    
    selected_date = st.date_input(
        "Mission Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )
    
    site_names = [s["name"] for s in sites_meta]
    selected_name = st.selectbox("Landing site", site_names, index=0)
    selected_site = next(s for s in sites_meta if s["name"] == selected_name)

    # Filter dataframe by selected date
    full_series = get_site_series(df, selected_site["id"])
    series = full_series[full_series["timestamp"].dt.date == selected_date].reset_index(drop=True)
    
    if series.empty:
        st.error("No data for this date.")
        st.stop()

    hours = series["timestamp"].dt.strftime("%H:%M").tolist()

    idx = st.select_slider(
        "Mission time (UTC)",
        options=list(range(len(series))),
        format_func=lambda i: hours[i],
        value=0,
    )

    st.divider()
    compare_mode = st.checkbox("🔍 Compare all sites (at this hour)")
    st.caption(
        "Dataset: 30 days of pre-calculated illumination & DTE visibility "
        "(modeled after LOLA/Mazarico et al.). 24h @ 1h resolution."
    )

    with st.expander("ℹ️ How the Go / No-Go engine works"):
        st.markdown(
            "**GO** - Sun above horizon **and** Earth visible simultaneously.  \n"
            "**CAUTION** - Only one of the two criteria is met.  \n"
            "**NO-GO** - Neither criterion met.\n\n"
            "Score weights strong solar input (>3 deg) at 50 pts and "
            "direct-to-Earth line of sight at 50 pts for a 0-100 readiness readout."
        )


# --- COMPARE MODE SECTION ---
if compare_mode:
    st.markdown(f"### ⚖️ Site Comparison ({selected_date} at {hours[idx]} UTC)")
    
    compare_rows = []
    for site in sites_meta:
        site_series = get_site_series(df, site["id"])
        site_day_series = site_series[site_series["timestamp"].dt.date == selected_date].reset_index(drop=True)
        
        if not site_day_series.empty:
            row = site_day_series.iloc[idx]
            verdict = evaluate_point(row)
            
            compare_rows.append({
                "Site": site["name"],
                "Sun Elev (deg)": f"{row['sun_elevation_deg']:+.1f}°",
                "Earth Visible": "✅ Yes" if row["earth_visible"] else "❌ No",
                "Power OK": "✅ Yes" if row["power_ok"] else "❌ No",
                "Status": verdict.status,
                "Readiness": f"{verdict.score}/100"
            })
    
    compare_df = pd.DataFrame(compare_rows)
    
    def color_status(val):
        if val == "GO": return 'background-color: #22C55E; color: white;'
        elif val == "CAUTION": return 'background-color: #F59E0B; color: white;'
        elif val == "NO-GO": return 'background-color: #EF4444; color: white;'
        return ''
    
    try:
        styled_df = compare_df.style.map(color_status, subset=['Status'])
    except AttributeError:
        styled_df = compare_df.style.applymap(color_status, subset=['Status'])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.divider()


# --- MAIN SINGLE SITE VIEW ---
row = series.iloc[idx]
verdict = evaluate_point(row)
summary = summary_for_site(series)


col_status, col_metrics = st.columns([1, 2], gap="large")

with col_status:
    st.markdown(
        f"""
        <div class="status-card" style="background: {verdict.color};">
            <p class="status-title">{verdict.status}</p>
            <p class="status-label">{verdict.label}</p>
            <p class="status-label" style="font-size:13px; opacity:0.85;">
                {selected_site['name']}<br>{selected_date} · {hours[idx]} UTC
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(verdict.score / 100.0, text=f"Readiness score: {verdict.score}/100")

with col_metrics:
    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Sun elevation",
        f"{row['sun_elevation_deg']:+.1f}°",
        delta="Power OK" if row["power_ok"] else "No power",
        delta_color="normal" if row["power_ok"] else "inverse",
    )
    m2.metric(
        "Earth visibility",
        "Visible" if row["earth_visible"] else "Blocked",
        delta="DTE link" if row["earth_visible"] else "No DTE",
        delta_color="normal" if row["earth_visible"] else "inverse",
    )
    m3.metric(
        "DTE streak (window)",
        f"{summary['comms_streak']} h",
        delta="Continuous link" if summary["comms_streak"] >= 2 else "Short link",
        delta_color="normal" if summary["comms_streak"] >= 2 else "off",
    )

    st.markdown("**Why this verdict?**")
    for r in verdict.reasons:
        st.markdown(f"- {r}")


st.markdown(f"### 🕒 Mission timeline ({selected_date})")
st.plotly_chart(
    timeline_status_chart(series, idx),
    use_container_width=True,
    config={"displayModeBar": False},
)


st.markdown("### 📊 Detailed telemetry")
chart_col1, chart_col2 = st.columns(2, gap="large")
with chart_col1:
    st.markdown("**☀️ Solar elevation vs. time**")
    st.plotly_chart(
        sun_elevation_chart(series, idx),
        use_container_width=True,
        config={"displayModeBar": False},
    )
with chart_col2:
    st.markdown("**📡 Earth visibility window**")
    st.plotly_chart(
        comms_window_chart(series, idx),
        use_container_width=True,
        config={"displayModeBar": False},
    )


st.markdown("### 🗺️ Candidate sites & mission notes")
map_col, notes_col = st.columns([1, 1], gap="large")

with map_col:
    st.plotly_chart(
        site_map_chart(sites_meta, selected_site["id"]),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with notes_col:
    st.markdown(f"#### {selected_site['name']}")
    st.caption(
        f"Lat {selected_site['lat']:.2f}° · Lon {selected_site['lon']:.2f}° · "
        f"Elev {selected_site['elevation_m']} m"
    )
    st.write(selected_site["description"])
    st.info(f"**Risk profile:** {selected_site['risk_notes']}")

    st.markdown(f"**Window summary ({selected_date})**")
    s1, s2, s3 = st.columns(3)
    s1.metric("GO hours", f"{summary['go_hours']}/{summary['total_hours']}")
    s2.metric("Power OK", f"{summary['power_pct']}%")
    s3.metric("DTE visible", f"{summary['comms_pct']}%")


st.divider()
st.caption(
    "Prototype for NASA Space Apps Challenge · Lunar Landing Site Navigator. "
    "Data spans 30 days and is modeled after public LOLA illumination studies - "
    "not for operational use."
)