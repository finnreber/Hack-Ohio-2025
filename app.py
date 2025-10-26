import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import streamlit as st
import requests

# Path setup
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

try:
    import compute_stress as cs
except Exception:
    cs = None

# Streamlit setup
st.set_page_config(page_title="Hawaii Grid", layout="wide")
st.markdown("""
<style>
:root {
  --bg:#0f1321; --panel:#131a2e; --muted:#0d1426;
  --text:#eef1ff; --sub:#a6b0d6; --accent:#7c5cff;
  --shadow:0 16px 40px rgba(0,0,0,.35); --radius:22px;
}
#MainMenu, footer, [data-testid="stToolbar"] {display:none!important;}
.stApp {
  background: radial-gradient(1200px 600px at 15% 10%, #151b31 0%, var(--bg) 40%, #0b1020 100%)!important;
}
.card {
  background:linear-gradient(180deg, var(--panel), var(--muted));
  border-radius:22px; padding:22px 24px; box-shadow:var(--shadow);
  border:1px solid rgba(255,255,255,.04); margin-bottom:20px;
}
h1,h2,h3,h4,h5,h6{color:var(--text)!important;}
.small{color:var(--sub); font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

# Background image helper
def draw_oahu_background(ax, buses_df, img_path="data/gis/honolulu.jpg", alpha=0.35):
    """Draw a white Oahu silhouette behind the network."""
    if not os.path.exists(img_path):
        st.warning(f"Oahu background image not found: {img_path}")
        return

    img = mpimg.imread(img_path)
    img_gray = np.mean(img[..., :3], axis=-1) if img.ndim == 3 else img
    img_inv = 1 - img_gray

    bxmin, bxmax = buses_df["x"].min(), buses_df["x"].max()
    bymin, bymax = buses_df["y"].min(), buses_df["y"].max()
    b_w, b_h = bxmax - bxmin, bymax - bymin

    pad_x, pad_y = b_w * 0.15, b_h * 0.15
    shift_x, shift_y = -b_w * 0.06, b_h * 0.02

    extent = [
        bxmin - pad_x + shift_x,
        bxmax + pad_x + shift_x,
        bymin - pad_y + shift_y,
        bymax + pad_y + shift_y
    ]

    ax.set_facecolor("black")
    ax.imshow(img_inv, extent=extent, aspect='auto', zorder=0, alpha=alpha, cmap="gray")

# Weather fetcher
def get_hawaii_weather():
    try:
        headers = {'User-Agent': 'HawaiiGridApp/1.0'}
        resp = requests.get("https://api.weather.gov/points/21.3069,-157.8583", headers=headers)
        data = resp.json()
        forecast_url = data['properties']['forecastHourly']
        resp = requests.get(forecast_url, headers=headers)
        weather = resp.json()['properties']['periods'][0]

        temp_f = weather['temperature']
        temp_c = (temp_f - 32) * 5 / 9
        wind_mph = float(''.join(filter(str.isdigit, weather['windSpeed'])))
        wind_ms = wind_mph * 0.44704
        wind_pct = min(100.0, (wind_ms / 15.0) * 100.0)
        return temp_c, wind_pct
    except Exception as e:
        st.error(f"Weather fetch failed: {e}")
        return None, None

# Data helpers
def csv_try(paths):
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    raise FileNotFoundError(paths)

def compute_edge_states(df_lines, temp_c, wind_pct):
    wind_ms = (wind_pct / 100.0) * 15.0
    if cs and hasattr(cs, "compute_stress"):
        try:
            out = cs.compute_stress(df_lines.copy(), temp_c, wind_ms)
        except Exception as e:
            st.warning(f"compute_stress failed: {e}")
            out = df_lines.copy()
            out["stress"] = 0
    else:
        out = df_lines.copy()
        out["stress"] = 0

    def stress_color(s):
        if s > 100: return "#8B0000"
        elif s > 90: return "#FF0000"
        elif s > 70: return "#FFA500"
        elif s > 50: return "#FFFF00"
        else: return "#00FF00"
    out["color"] = out["stress"].apply(stress_color)
    return out[["name", "stress", "color"]]

# Session State
if "temp" not in st.session_state: st.session_state["temp"] = 27.0
if "wind" not in st.session_state: st.session_state["wind"] = 50.0

# Layout
left, right = st.columns([0.35, 0.65])

with left:
    st.markdown("## 🌤️ Controls")

    if st.button("☀️ Import Current Hawaii Weather", use_container_width=True):
        temp_now, wind_now = get_hawaii_weather()
        if temp_now is not None:
            st.session_state["temp"], st.session_state["wind"] = temp_now, wind_now
            st.rerun()

    temp = st.slider("Temperature (°C)", 10.0, 75.0, st.session_state["temp"], key="temp_slider")
    wind = st.slider("Wind Intensity (%)", 0.0, 100.0, st.session_state["wind"], key="wind_slider")
    st.session_state["temp"], st.session_state["wind"] = temp, wind

# ───────────────────────────────
# Load and compute reactively
# ───────────────────────────────
buses = csv_try(["data/csv/buses.csv"])
lines = csv_try(["data/csv/lines.csv"])
lines = lines.rename(columns={"bus0": "bus_a", "bus1": "bus_b"})
lines["bus_a"] = lines["bus_a"].astype(str)
lines["bus_b"] = lines["bus_b"].astype(str)
buses["name"] = buses["name"].astype(str)

# Update line stresses
edge_states = compute_edge_states(lines, st.session_state["temp"], st.session_state["wind"])
lines_plot = lines.merge(edge_states, on="name", how="left")

incident = pd.concat([
    lines_plot[["bus_a", "name"]].rename(columns={"bus_a": "bus"}),
    lines_plot[["bus_b", "name"]].rename(columns={"bus_b": "bus"})
]).merge(edge_states, on="name", how="left")

node_stress = incident.groupby("bus")["stress"].max().rename("node_stress").reset_index()
buses_plot = buses.merge(node_stress, left_on="name", right_on="bus", how="left").fillna({"node_stress": 0.0})
buses_plot["node_color"] = buses_plot["node_stress"].apply(
    lambda s: "#00FF00" if s < 60 else "#FFA500" if s < 90 else "#FF0000"
)

# Alerts hub
with left:
    st.markdown("### ⚠️ Alert Hub")
    critical_lines = lines_plot[lines_plot["color"].isin(["#FF0000", "#8B0000"])]

    if critical_lines.empty:
        st.markdown("<div style='color:#00FF00;font-weight:600;'>✅ No current alerts detected.</div>", unsafe_allow_html=True)
    else:
        for _, row in critical_lines.iterrows():
            bus_a, bus_b = str(row.get("bus_a", "?")), str(row.get("bus_b", "?"))
            name_a = buses.loc[buses["name"] == bus_a, "BusName"].iloc[0] if "BusName" in buses.columns and (buses["name"] == bus_a).any() else bus_a
            name_b = buses.loc[buses["name"] == bus_b, "BusName"].iloc[0] if "BusName" in buses.columns and (buses["name"] == bus_b).any() else bus_b

            st.markdown(
                f"<div style='color:#FF0000;font-weight:600;'>🚨 {name_a} ↔ {name_b} — Critical Alert</div>",
                unsafe_allow_html=True
            )

# Plot network
with right:
    st.markdown(f"""
    <div class="card" style="display:flex; align-items:center; justify-content:space-between;">
      <div>
        <h1 style="margin:0;">Hawaii Grid</h1>
        <div class="small">Team 68 • Synthetic 37-bus network</div>
      </div>
      <div style="display:flex; gap:10px;">
        <div class="small" style="padding:10px 14px; border-radius:12px; background:#1a2140;">
          Wind <b style="color:#fff">{st.session_state["wind"]:.0f}%</b></div>
        <div class="small" style="padding:10px 14px; border-radius:12px; background:#1a2140;">
          Temp <b style="color:#fff">{st.session_state["temp"]:.0f}°C</b></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=120)
    fig.patch.set_facecolor("#131a2e")
    ax.set_facecolor("#131a2e")
    ax.axis("off")

    # Oahu Silhouette
    draw_oahu_background(ax, buses, img_path="data/gis/honolulu.jpg", alpha=0.35)

    b_coords = buses.set_index("name")[["x", "y"]]

    def xy(bus_id):
        try:
            return b_coords.loc[str(bus_id)].values
        except KeyError:
            return None

    for _, e in lines_plot.iterrows():
        a, b = xy(e["bus_a"]), xy(e["bus_b"])
        if a is None or b is None:
            continue
        color = e.get("color", "#00FF00")
        stress = float(e.get("stress", 0.0))
        width = max(1.8, 1.8 + 7.0 * (stress / 100.0))
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, linewidth=width,
                alpha=0.95, solid_capstyle="round", zorder=2)

    for _, r in buses_plot.iterrows():
        ax.scatter(r["x"], r["y"], s=220, color=r["node_color"],
                   edgecolors="white", linewidths=1.4, zorder=3)
        ax.text(r["x"], r["y"], str(r["name"]), fontsize=9,
                ha="center", va="center", color="white", zorder=4)

    st.pyplot(fig, use_container_width=True)
