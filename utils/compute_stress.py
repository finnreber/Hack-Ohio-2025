import numpy as np

def compute_stress(lines_df, temp, wind):
    T_MOT = 75   # Max conductor temperature (°C)
    T_ref = 25   # Reference ambient temp
    k_w = 0.05   # Wind cooling coefficient

    lines_df = lines_df.copy()
    I_base = lines_df["rating"]
    I_max = I_base * np.sqrt((T_MOT - temp) / (T_MOT - T_ref)) * (1 + k_w * wind)
    lines_df["stress"] = (I_base / I_max) * 100  # percent stress
    return lines_df