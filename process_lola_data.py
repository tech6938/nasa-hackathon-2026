import json
import rasterio
import numpy as np
from pathlib import Path

def process_nasa_dem(dem_filepath: str, output_json: str = "data/lola_terrain.json"):
    """
    NASA ke GeoTIFF DEM file ko padh kar 3D map ke liye JSON mein convert karta hai.
    """
    print(f"Reading NASA DEM file: {dem_filepath}")
    
    try:
        with rasterio.open(dem_filepath) as src:
            # Padhne ke liye ek chota hissa (south pole ke qareeb) select karein
            # Asal file bohot bari hoti hai (GBs mein), isliye hum subset padh rahe hain
            window = rasterio.windows.Window(0, 0, 50, 50) # 50x50 grid
            elevation = src.read(1, window=window)
            
            # No-data values ko handle karein (jo -9999 waghera hoti hain)
            elevation = np.where(elevation < -1000, 0, elevation)
            
            # Coordinates calculate karein (Lat/Lon)
            rows, cols = elevation.shape
            transform = src.transform
            
            lats = []
            lons = []
            for r in range(rows):
                row_lats = []
                row_lons = []
                for c in range(cols):
                    x, y = rasterio.transform.xy(transform, r, c)
                    row_lons.append(round(x, 4))
                    row_lats.append(round(y, 4))
                lats.append(row_lats)
                lons.append(row_lons)
            
            # JSON format mein save karein
            terrain_data = {
                "lats": lats,
                "lons": lons,
                "elevation": elevation.tolist()
            }
            
            with open(output_json, "w") as f:
                json.dump(terrain_data, f)
                
            print(f"✅ Success! Real NASA terrain data saved to {output_json}")
            print(f"Grid size: {rows}x{cols}")
            
    except Exception as e:
        print(f"❌ Error processing DEM: {e}")
        print("Make sure the file is a valid GeoTIFF (.tif) format.")

# --- Example Usage ---
if __name__ == "__main__":
    # 13 Nov ko NASA se jo .tif file milegi, uska path yahan dein
    # Example: process_nasa_dem("LDEM_85S_40M.tif")
    pass