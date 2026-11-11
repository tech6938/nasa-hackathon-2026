import json
import math
from datetime import datetime, timedelta

def generate_monthly_data():
    # Start date: Nov 14, 2026
    start_date = datetime(2026, 11, 14, 0, 0, 0)
    days = 30
    hours = 24
    
    sites = [
        {
            "id": "shackleton", "name": "Shackleton Crater - Connecting Ridge",
            "lat": -89.45, "lon": 136.67, "elevation_m": 1760,
            "description": "Near-continuous solar illumination, but Earth is largely blocked by the crater rim.",
            "risk_notes": "Power: EXCELLENT | Comms: POOR",
            "sun_base": 2.0, "sun_amp": 3.0, "earth_prob": 0.15
        },
        {
            "id": "malapert", "name": "Malapert Massif",
            "lat": -85.99, "lon": 357.07, "elevation_m": 5000,
            "description": "Elevated ridge with exceptional direct-to-Earth visibility. Solar exposure is variable.",
            "risk_notes": "Power: GOOD | Comms: EXCELLENT",
            "sun_base": 5.0, "sun_amp": 4.0, "earth_prob": 0.95
        },
        {
            "id": "nobile", "name": "Nobile Rim 1",
            "lat": -85.3, "lon": 43.0, "elevation_m": 2100,
            "description": "Balanced site. Moderate solar exposure and Earth visibility, with periodic outages.",
            "risk_notes": "Power: MODERATE | Comms: GOOD",
            "sun_base": 1.0, "sun_amp": 2.5, "earth_prob": 0.65
        },
        {
            "id": "degerlache", "name": "de Gerlache Rim",
            "lat": -88.5, "lon": 267.1, "elevation_m": 1400,
            "description": "Long alternating blocks of sunlight and shadow; Earth is periodically obscured.",
            "risk_notes": "Power: MIXED | Comms: FAIR",
            "sun_base": 0.5, "sun_amp": 3.5, "earth_prob": 0.40
        }
    ]

    output_data = {"metadata": {}, "sites": []}

    for site in sites:
        site_data = {k: v for k, v in site.items() if k not in ['sun_base', 'sun_amp', 'earth_prob']}
        site_data["timeseries"] = []
        
        for d in range(days):
            current_date = start_date + timedelta(days=d)
            
            # Simulate a 14-day lunar day/night cycle (roughly half the month is sunny, half is dark)
            # This shifts the sun phase across the month
            day_phase = math.sin((d / 14.0) * math.pi)
            
            for h in range(hours):
                current_time = current_date + timedelta(hours=h)
                timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # 1. Calculate Sun Elevation (Simulated)
                # Base + daily variation + monthly lunar cycle variation
                daily_var = math.sin((h / 24.0) * 2 * math.pi) * 1.5
                sun_elev = site["sun_base"] + (day_phase * site["sun_amp"]) + daily_var
                
                # Add slight noise
                sun_elev = round(sun_elev + (math.sin(h * d) * 0.5), 1)
                power_ok = sun_elev > 0.0
                
                # 2. Calculate Earth Visibility (Simulated)
                # Use a simple pseudo-random pattern based on the site's probability
                # (This creates realistic-looking "windows" of comms)
                pattern = math.sin((h * 0.5) + (d * 0.3) + site["lon"])
                earth_visible = pattern > (1.0 - site["earth_prob"] * 2)
                
                site_data["timeseries"].append({
                    "timestamp": timestamp,
                    "sun_elevation_deg": sun_elev,
                    "earth_visible": earth_visible,
                    "power_ok": power_ok
                })
        
        output_data["sites"].append(site_data)

    # Save to the JSON file
    with open('data/sites_data.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    print("✅ Successfully generated 30 days of data in data/sites_data.json")

if __name__ == "__main__":
    generate_monthly_data()