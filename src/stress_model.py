import pandas as pd
import math
from lib.ieee738.ieee738 import Conductor, ConductorParams

def compute_line_stress(lines_df, env_params):
    """
    Compute stress on each transmission line using IEEE-738-based thermal ratings.
    Returns a DataFrame with new columns: 'rating_mva', 'flow_mva', 'stress', 'color'
    """

    results = []

    for _, row in lines_df.iterrows():
        # Copy environmental parameters (ambient, wind, etc.)
        params = dict(env_params)

        # Conductor properties (robust fallbacks)
        params.update({
            "TLo": 25,
            "THi": 50,
            "RLo": float(row.get("RLo", 0.2708 / 5280)),  # ohm/ft
            "RHi": float(row.get("RHi", 0.2974 / 5280)),
            "Diameter": float(row.get("Diameter", 0.741)), # inches
            "Tc": float(row.get("MOT", 80)),               # °C
        })

        # Compute rating (Amps)
        try:
            cp = ConductorParams(**params)
            conductor = Conductor(cp)
            rating_amps = conductor.steady_state_thermal_rating()
        except Exception as e:
            print(f"[WARN] IEEE738 calc failed for {row.get('name', '?')}: {e}")
            rating_amps = 0

        # Convert to 3-phase MVA
        v_nom = float(row.get("v_nom", 138)) * 1e3  # Default 138 kV if missing
        rating_mva = math.sqrt(3) * rating_amps * v_nom * 1e-6

        # Actual line loading
        flow_mva = float(row.get("p0_nominal", 0))
        stress = flow_mva / rating_mva if rating_mva > 0 else 0

        # Color code thresholds
        if stress >= 1.0:
            color = "darkred"
        elif stress >= 0.9:
            color = "red"
        elif stress >= 0.7:
            color = "orange"
        elif stress >= 0.5:
            color = "yellow"
        else:
            color = "green"

        results.append({
            "name": row.get("name", "unknown"),
            "rating_mva": rating_mva,
            "flow_mva": flow_mva,
            "stress": stress,
            "color": color,
        })

    return pd.DataFrame(results)
