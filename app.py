import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

try:
    import compute_stress as cs   
except Exception:
    cs = None
try:
    import stress_model as sm     
except Exception:
    sm = None

st.set_page_config(page_title="Hawaii Grid", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root{ --bg:#0f1321; --panel:#131a2e; --muted:#0d1426; --text:#eef1ff; --sub:#a6b0d6; --accent:#7c5cff; --shadow:0 16px 40px rgba(0,0,0,.35); --radius:22px; }
#MainMenu, header[data-testid="stHeader"], footer, [data-testid="stToolbar"] { display:none!important; }
.stApp, .main, .block-container { background: radial-gradient(1200px 600px at 15% 10%, #151b31 0%, var(--bg) 40%, #0b1020 100%)!important; }
section[data-testid="stSidebar"]{ min-width:320px!important; max-width:320px!important; background:var(--panel)!important; color:var(--text)!important; box-shadow:var(--shadow); }
section[data-testid="stSidebar"] *{ color:var(--text)!important; }
[data-baseweb="slider"] div [role="slider"]{ box-shadow:0 0 0 6px rgba(124,92,255,.15)!important; background:var(--accent)!important; border:3px solid rgba(255,255,255,.15)!important; }
.card{ background:linear-gradient(180deg, var(--panel), var(--muted)); border-radius:22px; padding:22px 24px; box-shadow:var(--shadow); border:1px solid rgba(255,255,255,.04); }
h1,h2,h3,h4,h5,h6{ color:var(--text)!important; } .small{ color:var(--sub); font-size:.9rem; }
</style>
""", unsafe_allow_html=True)

import requests
import json

def get_hawaii_weather():
    """Fetch current weather in Honolulu, Hawaii using National Weather Service API"""
    try:
        headers = {'User-Agent': 'HawaiiGridApp/1.0'}
        point_url = "https://api.weather.gov/points/21.3069,-157.8583"
        response = requests.get(point_url, headers=headers)
        point_data = response.json()
        
        if response.status_code != 200:
            st.error("Could not find weather station data")
            return None, None
            
        forecast_url = point_data['properties']['forecastHourly']
        response = requests.get(forecast_url, headers=headers)
        weather_data = response.json()
        
        if response.status_code == 200:
            current = weather_data['properties']['periods'][0]
            
            # Convert temperature from F to C
            temp_f = current['temperature']
            temp_c = (temp_f - 32) * 5/9
            
            # Convert wind speed from mph to m/s and then to percentage
            # First extract the numeric wind speed from the string (e.g., "10 mph" -> 10)
            wind_mph = float(''.join(filter(str.isdigit, current['windSpeed'])))
            wind_ms = wind_mph * 0.44704  # Convert mph to m/s
            wind_pct = min(100.0, (wind_ms / 15.0) * 100.0)
            
            st.sidebar.info(f"Current conditions in Honolulu:\n" + 
                          f"Temperature: {temp_c:.1f}°C ({temp_f}°F)\n" +
                          f"Wind: {wind_ms:.1f} m/s ({wind_mph} mph)")
            
            return temp_c, wind_pct
        else:
            st.error("Could not fetch weather data")
            return None, None
    except Exception as e:
        st.error(f"Failed to fetch weather data: {str(e)}")
        return None, None

# Sidebar controls
st.sidebar.header("Adjust Parameters")

# Weather import button with custom styling
st.sidebar.markdown("""
    
""", unsafe_allow_html=True)

# Initialize session state if needed
if 'temp' not in st.session_state:
    st.session_state['temp'] = 27.0
if 'wind' not in st.session_state:
    st.session_state['wind'] = 50.0

# Define callback functions for slider updates
def on_temp_change():
    st.session_state['temp'] = st.session_state.temp_slider

def on_wind_change():
    st.session_state['wind'] = st.session_state.wind_slider

# Weather import button with loading state
# Make a big empty space for visual separation
st.sidebar.markdown("### ")

# Create a large, eye-catching button
if st.sidebar.button("🌤️ IMPORT CURRENT\nHAWAII WEATHER", use_container_width=True):
    with st.sidebar.status("Fetching weather data...", expanded=True) as status:
        current_temp, current_wind = get_hawaii_weather()
        if current_temp is not None and current_wind is not None:
            # Update session state
            st.session_state['temp'] = current_temp
            st.session_state['wind'] = current_wind
            # Force slider values to update
            st.session_state.temp_slider = current_temp
            st.session_state.wind_slider = current_wind
            status.update(label="Weather data imported!", state="complete", expanded=False)
            # Force rerun to update UI
            st.rerun()

# Sliders with keys for state management
wind = st.sidebar.slider("Wind Intensity (scaled %)", 0.0, 100.0, 
                        st.session_state['wind'], 
                        key='wind_slider',
                        on_change=on_wind_change)
temp = st.sidebar.slider("Temperature (°C)", 10.0, 75.0, 
                        st.session_state['temp'],
                        key='temp_slider',
                        on_change=on_temp_change)

st.markdown(
    f"""
    <div class="card" style="margin-bottom:18px; display:flex; align-items:center; justify-content:space-between;">
      <div>
        <h1 style="margin:0; letter-spacing:.3px;">Hawaii Grid</h1>
        <div class="small">Team 68 • Synthetic 37-bus network</div>
      </div>
      <div style="display:flex; gap:10px;">
        <div class="small" style="padding:10px 14px; border-radius:12px; background:#1a2140; border:1px solid rgba(255,255,255,.06);">
          Wind&nbsp;<b style="color:#fff">{wind:.0f}%</b>
        </div>
        <div class="small" style="padding:10px 14px; border-radius:12px; background:#1a2140; border:1px solid rgba(255,255,255,.06);">
          Temp&nbsp;<b style="color:#fff">{temp:.0f}°C</b>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Helpers
def csv_try(paths):
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    raise FileNotFoundError(paths)

# Build an undirected topology from bus positions (k-NN) when no lines file
def lines_from_buses_knn(buses_df: pd.DataFrame, k: int = 2) -> pd.DataFrame:
    B = buses_df.copy()
    B["name"] = B["name"].astype(str)
    coords = B[["x","y"]].to_numpy(dtype=float)
    ids = B["name"].tolist()

    dists = np.sqrt(((coords[:,None,:] - coords[None,:,:])**2).sum(axis=2))
    np.fill_diagonal(dists, np.inf)

    edges = set()
    for i, src in enumerate(ids):
        nbr_idx = np.argsort(dists[i])[:k]
        for j in nbr_idx:
            a, b = sorted((src, ids[j]), key=str)
            if a != b: edges.add((a,b))

    lines = pd.DataFrame(sorted(edges), columns=["bus_a","bus_b"])
    lines.insert(0, "name", [f"L{i}" for i in range(len(lines))])
    return lines

def load_lines(buses_df: pd.DataFrame) -> pd.DataFrame:
    """Use real endpoints if available; else synthesize from buses via kNN.
       Also left-join optional p0_nominal from line_flows_nominal.csv."""
    # 1) try files with endpoints
    for p in ["data/lines.csv", "data/csv/lines.csv"]:
        if os.path.exists(p):
            df = pd.read_csv(p).copy()
            colmap = {}
            if "from" in df.columns and "bus_a" not in df.columns: colmap["from"] = "bus_a"
            if "to"   in df.columns and "bus_b" not in df.columns: colmap["to"]   = "bus_b"
            if "bus0" in df.columns and "bus_a" not in df.columns: colmap["bus0"] = "bus_a"
            if "bus1" in df.columns and "bus_b" not in df.columns: colmap["bus1"] = "bus_b"
            if colmap: df = df.rename(columns=colmap)
            if "name" not in df.columns:
                df.insert(0, "name", [f"L{i}" for i in range(len(df))])
            for c in ["name","bus_a","bus_b"]:
                df[c] = df[c].astype(str)
            # Include rating/s_nom and other needed columns if they exist
            needed_cols = ["name", "bus_a", "bus_b"]
            for col in ["rating", "s_nom"]:
                if col in df.columns:
                    needed_cols.append(col)
            lines = df[needed_cols].copy()
            break
    else:
        # 2) synthesize if we don't have endpoints
        lines = lines_from_buses_knn(buses_df, k=2)
        # Add default rating if synthesizing
        if "rating" not in lines.columns and "s_nom" not in lines.columns:
            lines["rating"] = 200.0  # default MVA rating

    # 3) optional nominal flows
    for p in ["data/line_flows_nominal.csv", "data/csv/line_flows_nominal.csv"]:
        if os.path.exists(p):
            flows = pd.read_csv(p).copy()
            if {"name","p0_nominal"} <= set(flows.columns):
                flows["name"] = flows["name"].astype(str)
                lines = lines.merge(flows[["name","p0_nominal"]], on="name", how="left")
            break

    return lines

def compute_edge_states(df_lines: pd.DataFrame, temp_c: float, wind_pct: float) -> pd.DataFrame:
    """Call your backend. Expect columns: name, stress(0..100), color."""
    out = None
    # Convert wind percentage to m/s (assuming 0-100% maps to 0-15 m/s)
    wind_ms = (wind_pct / 100.0) * 15.0
    
    if cs and hasattr(cs, "compute_stress"):
        try:
            out = cs.compute_stress(df_lines.copy(), temp_c, wind_ms)
        except Exception as e:
            st.warning(f"compute_stress failed: {e}")
    if out is None and sm and hasattr(sm, "compute_line_stress"):
        try:
            out = sm.compute_line_stress(df_lines.copy(), {
                "temp": temp_c,
                "wind": wind_ms,  # Pass wind speed in m/s
                "pressure": 101.325,  # Standard atmospheric pressure (kPa)
                "elevation": 0.0,  # Sea level
                "latitude": 21.3069,  # Hawaii latitude
                "hour": 12.0,  # Noon
                "date": 180,  # Mid-year
                "atmosphere": "clear"  # Clear sky
            })
        except Exception as e:
            st.warning(f"compute_stress failed: {e}")
    if out is None and sm and hasattr(sm, "compute_line_stress"):
        try:
            out = sm.compute_line_stress(df_lines.copy(), {"temp": temp_c, "wind": wind_pct})
        except Exception as e:
            st.error(f"stress_model failed: {e}")
            out = None

    if isinstance(out, pd.DataFrame):
        out = out.copy()
        if "name" not in out.columns and "line_id" in out.columns:
            out.rename(columns={"line_id":"name"}, inplace=True)
        out["name"] = out["name"].astype(str)
        # normalize stress
        if "stress" not in out.columns:
            if "stress_pct" in out.columns: out["stress"] = out["stress_pct"]
            elif "utilization" in out.columns: out["stress"] = 100*out["utilization"]
            else: out["stress"] = 0.0
        if out["stress"].max() <= 1.5:
            out["stress"] = (out["stress"]*100).clip(0, 300)
        # colors if backend didn't supply
        if "color" not in out.columns:
            def to_color(s):
                return ("#27ae60" if s < 60 else  # Nominal - Green
                        "#f39c12" if s < 90 else  # Caution - Orange
                        "#c0392b")                # Critical - Red
            out["color"] = out["stress"].apply(to_color)
        return out[["name","stress","color"]]
    else:
        # neutral default
        tmp = df_lines.copy()
        tmp["name"] = tmp["name"].astype(str)
        tmp["stress"] = 0.0
        tmp["color"]  = "#8a93b6"
        return tmp[["name","stress","color"]]

# Load data
buses = csv_try(["data/buses.csv", "data/csv/buses.csv"]).copy()
buses["name"] = buses["name"].astype(str)

lines = load_lines(buses)
edge_states = compute_edge_states(lines, temp, wind)

# Node thresholds
incident = (
    pd.concat([
        lines[["bus_a","name"]].rename(columns={"bus_a":"bus"}),
        lines[["bus_b","name"]].rename(columns={"bus_b":"bus"})
    ], ignore_index=True)
    .merge(edge_states, on="name", how="left")
)
node_stress = incident.groupby("bus")["stress"].max().rename("node_stress").reset_index()

buses_plot = buses.merge(node_stress, left_on="name", right_on="bus", how="left")
buses_plot["node_stress"] = buses_plot["node_stress"].fillna(0.0)

def node_color(s):
    return ("#27ae60" if s < 60 else  # Nominal - Green
            "#f39c12" if s < 90 else  # Caution - Orange
            "#c0392b")                 # Critical - Red
buses_plot["node_color"] = buses_plot["node_stress"].apply(node_color)

lines_plot = lines.merge(edge_states, on="name", how="left")

# ── Plot (no axes; bigger nodes; edge width by stress; color by backend) ─────
fig, ax = plt.subplots(figsize=(12.5, 8), dpi=120)
bg = "#131a2e"; textc = "#e9ecff"
fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
ax.axis("off")

b_coords = buses.set_index("name")[["x","y"]]

def xy(bus_id):
    try:
        return b_coords.loc[str(bus_id)].values
    except Exception:
        return None

# draw edges
for _, e in lines_plot.iterrows():
    a = xy(e["bus_a"]); b = xy(e["bus_b"])
    if a is None or b is None: continue
    x1,y1 = a; x2,y2 = b
    color = e.get("color", "#8a93b6")
    stress = float(e.get("stress", 0.0))
    width = max(1.8, 1.8 + 7.0*(stress/100.0))
    ax.plot([x1,x2],[y1,y2], color=color, linewidth=width, zorder=1, alpha=.95, solid_capstyle="round")

# draw nodes (bigger)
for _, r in buses_plot.iterrows():
    size = 260 if float(r.get("v_nom", 69.0)) == 138.0 else 220
    ax.scatter(r["x"], r["y"], s=size, color=r["node_color"],
               edgecolors='white', linewidths=1.4, zorder=3)
    ax.text(r["x"], r["y"], str(r["name"]), fontsize=9, ha='center', va='center',
            color='white', zorder=4)

# optional compact legend
from matplotlib.lines import Line2D
legend = [
    Line2D([0],[0], marker='o', color='w', label='Nominal (<60%)', markerfacecolor="#27ae60",
           markeredgecolor='white', markeredgewidth=1, markersize=12),
    Line2D([0],[0], marker='o', color='w', label='Caution (60-90%)', markerfacecolor="#f39c12",
           markeredgecolor='white', markeredgewidth=1, markersize=12),
    Line2D([0],[0], marker='o', color='w', label='Critical (>90%)', markerfacecolor="#c0392b",
           markeredgecolor='white', markeredgewidth=1, markersize=12),
]
leg = ax.legend(handles=legend, loc='upper right', frameon=True)
leg.get_frame().set_facecolor("#1a2140"); leg.get_frame().set_edgecolor("none")
for t in leg.get_texts(): t.set_color(textc)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.pyplot(fig, width='stretch')
st.markdown('</div>', unsafe_allow_html=True)
