"""All Plotly figure builders."""
import plotly.graph_objects as go
import pandas as pd


def sun_elevation_chart(series: pd.DataFrame, current_idx: int) -> go.Figure:
    fig = go.Figure()
    fig.add_hrect(y0=3.0, y1=10, fillcolor="rgba(34,197,94,0.10)", line_width=0,
                  annotation_text="Strong solar", annotation_position="top left")
    fig.add_hrect(y0=0.0, y1=3.0, fillcolor="rgba(245,158,11,0.10)", line_width=0,
                  annotation_text="Marginal solar", annotation_position="top left")
    fig.add_hrect(y0=-10, y1=0.0, fillcolor="rgba(239,68,68,0.10)", line_width=0,
                  annotation_text="Shadow", annotation_position="bottom left")
    fig.add_trace(go.Scatter(
        x=series["timestamp"], y=series["sun_elevation_deg"],
        mode="lines+markers", name="Sun elevation",
        line=dict(color="#FBBF24", width=3),
        marker=dict(size=6),
        hovertemplate="%{x|%H:%M} UTC<br>Sun: %{y:.1f} deg<extra></extra>",
    ))
    row = series.iloc[current_idx]
    fig.add_trace(go.Scatter(
        x=[row["timestamp"]], y=[row["sun_elevation_deg"]],
        mode="markers",
        marker=dict(size=16, color="#38BDF8", line=dict(color="white", width=2)),
        name="Selected hour", hoverinfo="skip",
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Sun elevation (deg)", xaxis_title="Time (UTC)",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def comms_window_chart(series: pd.DataFrame, current_idx: int) -> go.Figure:
    colors = ["#22C55E" if v else "#EF4444" for v in series["earth_visible"]]
    labels = ["Visible" if v else "Blocked" for v in series["earth_visible"]]
    fig = go.Figure(go.Bar(
        x=series["timestamp"], y=[1] * len(series),
        marker_color=colors, text=labels, textposition="inside",
        textfont=dict(color="white", size=10),
        hovertemplate="%{x|%H:%M} UTC<br>%{text}<extra></extra>",
    ))
    row = series.iloc[current_idx]
    fig.add_trace(go.Scatter(
        x=[row["timestamp"]], y=[1.15],
        mode="markers",
        marker=dict(symbol="triangle-down", size=14, color="#38BDF8"),
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(showticklabels=False, range=[0, 1.25]),
        xaxis_title="Time (UTC)", showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def timeline_status_chart(series: pd.DataFrame, current_idx: int) -> go.Figure:
    colors, texts = [], []
    for _, r in series.iterrows():
        if r["power_ok"] and r["earth_visible"]:
            colors.append("#22C55E"); texts.append("GO")
        elif r["power_ok"] or r["earth_visible"]:
            colors.append("#F59E0B"); texts.append("CAUTION")
        else:
            colors.append("#EF4444"); texts.append("NO-GO")
    fig = go.Figure(go.Bar(
        x=series["timestamp"], y=[1] * len(series),
        marker_color=colors, text=texts, textposition="inside",
        textfont=dict(color="white", size=9),
        hovertemplate="%{x|%H:%M} UTC<br>%{text}<extra></extra>",
    ))
    row = series.iloc[current_idx]
    fig.add_trace(go.Scatter(
        x=[row["timestamp"]], y=[1.2],
        mode="markers",
        marker=dict(symbol="triangle-down", size=12, color="#38BDF8"),
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        height=170, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(showticklabels=False, range=[0, 1.3]),
        xaxis_title="24-hour mission timeline (UTC)",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def site_map_chart(sites_meta: list[dict], selected_id: str) -> go.Figure:
    lats = [s["lat"] for s in sites_meta]
    lons = [s["lon"] for s in sites_meta]
    names = [s["name"] for s in sites_meta]
    colors = ["#38BDF8" if s["id"] == selected_id else "#94A3B8" for s in sites_meta]
    sizes = [18 if s["id"] == selected_id else 10 for s in sites_meta]
    fig = go.Figure(go.Scatter(
        x=lons, y=lats, mode="markers+text",
        marker=dict(size=sizes, color=colors, line=dict(color="white", width=1)),
        text=names, textposition="top center",
        textfont=dict(size=9, color="white"),
        hovertemplate="<b>%{text}</b><br>Lat: %{y:.2f} deg<br>Lon: %{x:.2f} deg<extra></extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Longitude (degE)", range=[-180, 180], zeroline=True),
        yaxis=dict(title="Latitude (deg)", range=[-90, -80], zeroline=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig
