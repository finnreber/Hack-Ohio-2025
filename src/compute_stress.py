import numpy as np
import pandas as pd

def compute_stress(lines_df: pd.DataFrame, temp: float, wind: float) -> pd.DataFrame:
    """
    Compute stress level on transmission lines based on ambient temperature and wind speed.
    Lines now respond individually to environmental changes — only some are affected strongly.
    """

    lines_df = lines_df.copy()

    # Constants
    T_MOT = 75
    T_ref = 25
    k_w = 0.04

    # Ensure columns exist
    if "s_nom" in lines_df.columns:
        lines_df.rename(columns={"s_nom": "rating"}, inplace=True)
    if "rating" not in lines_df.columns:
        lines_df["rating"] = 200.0
    if "p0_nominal" not in lines_df.columns:
        lines_df["p0_nominal"] = 0.0

    # --- Per-line variation setup ---
    # Some lines are more sensitive to environment (weaker conductors or higher baseline load)
    rng = np.random.default_rng(seed=42)
    lines_df["sensitivity"] = rng.uniform(0.3, 1.2, size=len(lines_df))  # 0.3–1.2× sensitivity
    lines_df["base_load_factor"] = rng.uniform(0.3, 0.8, size=len(lines_df))  # baseline utilization

    # If p0_nominal all zeros, create per-line values that vary differently with sliders
    if (lines_df["p0_nominal"] == 0).all():
        # Temperature increases load, wind cools (reduces load)
        lines_df["p0_nominal"] = (
            lines_df["rating"]
            * (lines_df["base_load_factor"]
               + lines_df["sensitivity"] * (0.01 * (temp - 25) - 0.005 * wind))
        ).clip(lower=0.0)

    # Compute dynamic rating (cooling effect)
    lines_df["rating_dynamic"] = (
        lines_df["rating"]
        * np.sqrt((T_MOT - temp) / (T_MOT - T_ref))
        * (1 + k_w * wind)
    ).clip(lower=1e-3)

    # Stress (percentage)
    lines_df["stress"] = (lines_df["p0_nominal"] / lines_df["rating_dynamic"]) * 100
    lines_df["stress"] = lines_df["stress"].fillna(0).clip(0, 200)

    # Color mapping
    def stress_color(s):
        if s > 100: return "#8B0000"
        elif s > 90: return "#FF0000"
        elif s > 70: return "#FFA500"
        elif s > 50: return "#FFFF00"
        else: return "#00FF00"

    lines_df["color"] = lines_df["stress"].apply(stress_color)
    return lines_df[["name", "rating_dynamic", "p0_nominal", "stress", "color"]]