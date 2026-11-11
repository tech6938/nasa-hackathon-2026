# Lunar Landing Site Navigator

A Go / No-Go risk dashboard for candidate Artemis lunar south-pole landing sites.
Built for the NASA Space Apps Challenge - Lunar Landing Site Navigator.

## Why
Artemis mission planners must balance two competing constraints:
1. Solar power availability - the Sun must be above the horizon.
2. Direct-to-Earth communication - Earth must not be occluded by crater walls.

## Sites included (pre-calculated data)
- Shackleton Crater - Connecting Ridge
- Malapert Massif
- Nobile Rim 1
- de Gerlache Rim

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

Open http://localhost:8501.

## Architecture
    app.py                 -> UI orchestration
    src/data_loader.py     -> JSON to DataFrame (cached)
    src/logic.py           -> Go/No-Go decision engine + scoring
    src/charts.py          -> Plotly figure builders
    data/sites_data.json   -> 24h pre-calculated illumination & DTE visibility
    assets/style.css       -> dashboard styling

## Go / No-Go engine
- GO       - Sun above horizon AND Earth visible
- CAUTION  - only one criterion met
- NO-GO    - neither criterion met

Readiness score 0-100 weights solar input (>3 deg: +50, 1.5-3 deg: +35, 0-1.5 deg: +20)
and direct-to-Earth line of sight (+50).
