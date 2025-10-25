import numpy as np
import pandas as pd

def compute_stress(lines_df: pd.DataFrame, temp: float, wind: float) -> pd.DataFrame:
    """
    Compute stress level on transmission lines based on ambient temperature and wind speed.
    Simplified IEEE-738-inspired thermal derating model for real-time interactivity.

    Parameters
    ----------
    lines_df : pd.DataFrame
        Must include a 's_nom' or 'rating' column (MVA rating under nominal conditions)
        and a 'p0_nominal' column for power flow (MVA).
    temp : float
        Ambient temperature (°C).
    wind : float
        Wind speed (m/s).

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns: 'rating_dynamic', 'stress', and 'color'.
    """

    lines_df = lines_df.copy()

    # Constants for derating formula
    T_MOT = 75     # Max allowable conductor temperature (°C)
    T_ref = 25     # Reference ambient temperature (°C)
    k_w = 0.04     # Wind cooling coefficient (dimensionless)

    # Ensure required columns exist
    if "s_nom" in lines_df.columns:
        lines_df.rename(columns={"s_nom": "rating"}, inplace=True)
    if "p0_nominal" not in lines_df.columns:
        lines_df["p0_nominal"] = 0.0

    # Compute dynamic rating as a function of temp & wind
    lines_df["rating_dynamic"] = (
        lines_df["rating"]
        * np.sqrt((T_MOT - temp) / (T_MOT - T_ref))
        * (1 + k_w * wind)
    ).clip(lower=0)

    # Stress as % of available rating
    lines_df["stress"] = np.where(
        lines_df["rating_dynamic"] > 0,
        (lines_df["p0_nominal"] / lines_df["rating_dynamic"]) * 100,
        0,
    )

    # Color scale for visualization
    def stress_color(stress):
        if stress > 100:
            return "darkred"   # overloaded
        elif stress > 90:
            return "red"
        elif stress > 70:
            return "orange"
        elif stress > 50:
            return "yellow"
        else:
            return "green"

    lines_df["color"] = lines_df["stress"].apply(stress_color)

    return lines_df[["name", "rating_dynamic", "p0_nominal", "stress", "color"]]
