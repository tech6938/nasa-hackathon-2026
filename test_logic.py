from src.logic import evaluate_point
import pandas as pd

# Test 1: Perfect GO (Sun > 0, Earth Visible)
row_go = pd.Series({"sun_elevation_deg": 5.0, "power_ok": True, "earth_visible": True})
print("Test 1 (GO):", evaluate_point(row_go).status) 

# Test 2: CAUTION (Sun > 0, Earth Blocked)
row_caution = pd.Series({"sun_elevation_deg": 5.0, "power_ok": True, "earth_visible": False})
print("Test 2 (CAUTION):", evaluate_point(row_caution).status)

# Test 3: NO-GO (Sun < 0, Earth Blocked)
row_nogo = pd.Series({"sun_elevation_deg": -2.0, "power_ok": False, "earth_visible": False})
print("Test 3 (NO-GO):", evaluate_point(row_nogo).status)