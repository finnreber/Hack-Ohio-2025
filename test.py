import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


from src.data_loader import load_data
from src.compute_stress import compute_stress
from src.stress_model import compute_line_stress

# Load your data
lines, flows, buses, g_lines, g_buses = load_data()

# Merge nominal flows
lines_merged = lines.merge(flows, on="name", how="left")

# Environment for IEEE-738 model
env_params = {
    "Ta": 30,
    "WindVelocity": 2.0,
    "WindAngleDeg": 90,
    "SunTime": 12,
    "Elevation": 1000,
    "Latitude": 21,
    "Emissivity": 0.8,
    "Absorptivity": 0.8,
    "Direction": "EastWest",
    "Atmosphere": "Clear",
    "Date": "12 Jun",
}

# Simplified model
simple = compute_stress(lines_merged, temp=35, wind=1.0)
print("=== Simplified model ===")
print(simple.head())

# IEEE-738 physical model
accurate = compute_line_stress(lines_merged, env_params)
print("\n=== IEEE-738 model ===")
print(accurate.head())
