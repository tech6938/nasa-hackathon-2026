"""All Plotly figure builders."""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import os


def sun_elevation_chart(series: pd.DataFrame, current_idx: int) -> go.Figure:
    fig = go.Figure()
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.1, y0=0.1, x1=0.9, y1=0.9,
        line=dict(color="#EF4444", width=3, dash="dash"),
        fillcolor="rgba(0,0,0,0)",
    )
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
        marker_color=colors, text=labels, textposition="none",
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


def horizon_sky_chart(row: pd.Series) -> go.Figure:
    """A literal sky-dome visualization of the Sun relative to the horizon."""
    sun_deg = float(row["sun_elevation_deg"])
    
    fig = go.Figure()

    # 1. The Sky Dome Background (Green above horizon, Red below)
    fig.add_trace(go.Scatterpolar(
        r=[10, 10, -5, -5, 10],
        theta=[0, 360, 360, 0, 0],
        fill='toself',
        fillcolor='rgba(34, 197, 94, 0.1)' if sun_deg > 0 else 'rgba(239, 68, 68, 0.1)',
        line=dict(color='rgba(255,255,255,0.1)'),
        hoverinfo='skip',
        showlegend=False
    ))

    # 2. The Horizon Line (0 degrees)
    fig.add_trace(go.Scatterpolar(
        r=[0, 0],
        theta=[0, 360],
        mode='lines',
        line=dict(color='#EF4444', width=3, dash='dash'),
        name='Horizon (0°)',
        hoverinfo='skip'
    ))

    # 3. The Sun
    fig.add_trace(go.Scatterpolar(
        r=[max(sun_deg, -4.5)], 
        theta=[180], 
        mode='markers+text',
        marker=dict(size=18, color='#FBBF24', line=dict(color='white', width=2)),
        text=["☀️ Sun"],
        textposition="bottom center",
        name='Sun Position',
        hovertemplate=f"Sun Elevation: {sun_deg:+.1f}°<extra></extra>"
    ))

    fig.update_layout(
        height=340,
        margin=dict(l=40, r=40, t=40, b=40),
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[-6, 6], 
                showticklabels=False, 
                ticks=''
            ),
            angularaxis=dict(
                visible=False, 
                rotation=90, 
                direction="clockwise"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# --- 3D LUNAR MAP (Now supports NASA Data) ---
def lunar_3d_map(sites_meta: list[dict], selected_id: str, sun_deg: float) -> go.Figure:
    """A 3D surface plot of the lunar south pole with site markers and sun position."""
    fig = go.Figure()

    # Check if real NASA LOLA data exists
    if os.path.exists("data/lola_terrain.json"):
        try:
            with open("data/lola_terrain.json", "r") as f:
                terrain = json.load(f)
            X = np.array(terrain["lons"])
            Y = np.array(terrain["lats"])
            Z = np.array(terrain["elevation"])
            print("✅ Using Real NASA LOLA Terrain Data")
        except Exception as e:
            print(f"Error loading NASA data: {e}. Falling back to mock terrain.")
            os.remove("data/lola_terrain.json") # Delete corrupt file
            return lunar_3d_map(sites_meta, selected_id, sun_deg)
    else:
        # Fallback to mock terrain
        x = np.linspace(-90, -80, 50)
        y = np.linspace(-180, 180, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X * 1.5) * np.cos(Y * 0.5) * 3000 + 1000
        print("⚠️ Using Mock Terrain (NASA data not found)")

    # 3D Terrain
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale='Greys',
        showscale=False,
        opacity=0.8,
        hoverinfo='skip',
        name='Lunar Terrain'
    ))

    site_lats = [s["lat"] for s in sites_meta]
    site_lons = [s["lon"] for s in sites_meta]
    site_names = [s["name"] for s in sites_meta]
    
    # Estimate site Z based on the terrain function
    if not os.path.exists("data/lola_terrain.json"):
        site_z = np.sin(np.array(site_lats) * 1.5) * np.cos(np.array(site_lons) * 0.5) * 3000 + 1000
    else:
        # If using real data, just place markers slightly above the highest peak
        site_z = np.full(len(site_lats), np.max(Z) + 100)

    colors = ["#38BDF8" if s["id"] == selected_id else "#94A3B8" for s in sites_meta]
    sizes = [10 if s["id"] == selected_id else 5 for s in sites_meta]

    # Site Markers
    fig.add_trace(go.Scatter3d(
        x=site_lats, y=site_lons, z=site_z,
        mode='markers+text',
        marker=dict(size=sizes, color=colors, line=dict(color='white', width=1)),
        text=site_names,
        textposition="top center",
        textfont=dict(size=10, color="white"),
        name='Landing Sites',
        hovertemplate="<b>%{text}</b><br>Lat: %{x:.2f}<br>Lon: %{y:.2f}<extra></extra>"
    ))

    # Sun Marker
    fig.add_trace(go.Scatter3d(
        x=[-85], y=[0], z=[np.max(Z) + 5000],
        mode='markers+text',
        marker=dict(size=15, color='#FBBF24', symbol='circle'),
        text=[f"☀️ Sun ({sun_deg:+.1f}°)"],
        textposition="bottom center",
        textfont=dict(size=12, color="#FBBF24"),
        name='Sun',
        hoverinfo='skip'
    ))

    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(title="Longitude", showgrid=False, showticklabels=False, backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(title="Latitude", showgrid=False, showticklabels=False, backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(title="Elevation (m)", showgrid=False, showticklabels=False, backgroundcolor="rgba(0,0,0,0)"),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        showlegend=False
    )
    return fig