import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Hawaii Grid", layout="wide", initial_sidebar_state="expanded")

# ── Theme / CSS (dark, single accent) ─────────────────────────────────────────
st.markdown("""
<style>
:root{
  --bg: #0f1321;         /* app background */
  --panel: #131a2e;      /* cards / panels */
  --muted: #0d1426;      /* deeper panels */
  --text: #eef1ff;       /* primary text */
  --sub: #a6b0d6;        /* secondary text */
  --accent: #7c5cff;     /* single accent color */
  --shadow: 0 16px 40px rgba(0,0,0,.35);
  --radius: 22px;
}

/* Hide Streamlit chrome (top bar, menu, footer) */
#MainMenu, header[data-testid="stHeader"], footer, [data-testid="stToolbar"] { display: none !important; }

/* App background */
.stApp, .main, .block-container { background: radial-gradient(1200px 600px at 15% 10%, #151b31 0%, var(--bg) 40%, #0b1020 100%) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  color: var(--text) !important;
  box-shadow: var(--shadow);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p  { color: var(--text) !important; }

/* Sliders (WebKit + Firefox) */
[data-baseweb="slider"] div [role="slider"] {
  box-shadow: 0 0 0 6px rgba(124,92,255,.15) !important;
  background: var(--accent) !important;
  border: 3px solid rgba(255,255,255,.15) !important;
}
[data-baseweb="slider"] .css-19z3p3i, [data-baseweb="slider"] .css-14xtw13 {
  background: linear-gradient(90deg, var(--accent) 0%, #a890ff 100%) !important;
}

/* Cards */
.card {
  background: linear-gradient(180deg, var(--panel), var(--muted));
  border-radius: var(--radius);
  padding: 22px 24px;
  box-shadow: var(--shadow);
  border: 1px solid rgba(255,255,255,.04);
}

/* Titles / text */
h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }
.small { color: var(--sub); font-size: .9rem; }

/* Buttons (if you add any) */
.stButton > button {
  background: var(--accent) !important;
  color: white !important;
  border: none !important;
  border-radius: 14px !important;
  padding: 10px 16px !important;
  box-shadow: 0 10px 24px rgba(124,92,255,.35);
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar controls ──────────────────────────────────────────────────────────
st.sidebar.header("Adjust Parameters")
wind = st.sidebar.slider("Wind Intensity", 0.0, 100.0, 50.0)
temp = st.sidebar.slider("Temperature (°C)", 10.0, 40.0, 27.0)

# ── Title row (in-app, not Streamlit header) ──────────────────────────────────
st.markdown(
    """
    <div class="card" style="margin-bottom:18px; display:flex; align-items:center; justify-content:space-between;">
      <div>
        <h1 style="margin:0; letter-spacing:.3px;">Hawaii Grid</h1>
        <div class="small">Team 68 • Synthetic 37-bus network</div>
      </div>
      <div style="display:flex; gap:10px;">
        <div class="small" style="padding:10px 14px; border-radius:12px; background:#1a2140; border:1px solid rgba(255,255,255,.06);">
          Wind&nbsp;<b style="color:#fff">{:.0f}%</b>
        </div>
        <div class="small" style="padding:10px 14px; border-radius:12px; background:#1a2140; border:1px solid rgba(255,255,255,.06);">
          Temp&nbsp;<b style="color:#fff">{:.0f}°C</b>
        </div>
      </div>
    </div>
    """.format(wind, temp),
    unsafe_allow_html=True
)

# ── Data ──────────────────────────────────────────────────────────────────────
buses = pd.read_csv("data/buses.csv")

# connections placeholder; replace with real mapping if available
connections = [(i, i+1) for i in range(1, 37)]

# ── Plot (dark styling to match dashboard) ────────────────────────────────────
fig, ax = plt.subplots(figsize=(12.5, 8), dpi=120)

# colors consistent with theme
bg = "#131a2e"          # panel
gridc = "#2a3352"
textc = "#e9ecff"
accent = "#7c5cff"

fig.patch.set_facecolor(bg)
ax.set_facecolor(bg)

# light grid
ax.grid(True, color=gridc, linewidth=0.6, alpha=0.6)
for spine in ax.spines.values():
    spine.set_color("#3a4470")
    spine.set_linewidth(1.0)

ax.set_title("Hawaii Synthetic Grid – 37 Buses", fontsize=16, color=textc, pad=12)
ax.set_xlabel("Longitude", color=textc)
ax.set_ylabel("Latitude", color=textc)
ax.tick_params(colors="#c4c9ee")

# connections
for a, b in connections:
    try:
        x1, y1 = buses.loc[buses["name"] == a, ["x", "y"]].values[0]
        x2, y2 = buses.loc[buses["name"] == b, ["x", "y"]].values[0]
        ax.plot([x1, x2], [y1, y2], color="#8a93b6", linewidth=1.2, zorder=1, alpha=.9)
    except IndexError:
        continue

# buses (use accent for 138 kV, desaturated green for 69 kV to keep palette tight)
for _, row in buses.iterrows():
    c = accent if row["v_nom"] == 138.0 else "#53d19d"
    ax.scatter(row["x"], row["y"], color=c, s=90, edgecolors='white', linewidths=1, zorder=2)
    ax.text(row["x"], row["y"], str(int(row["name"])), fontsize=8, ha='center', va='center', color='white', zorder=3)

# legend styled like a pill
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='138 kV', markerfacecolor=accent, markeredgecolor='white', markeredgewidth=1, markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='69 kV', markerfacecolor='#53d19d', markeredgecolor='white', markeredgewidth=1, markersize=10),
    plt.Line2D([0], [0], color="#8a93b6", lw=2, label='Transmission Line')
]
leg = ax.legend(handles=legend_elements, loc='upper right', frameon=True)
leg.get_frame().set_facecolor("#1a2140")
leg.get_frame().set_edgecolor("none")
for text in leg.get_texts():
    text.set_color(textc)

# ── Display inside a "card" ───────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.pyplot(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
