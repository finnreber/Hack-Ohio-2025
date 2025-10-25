import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Hawaii Grid", layout="wide")

# ── Theme / CSS (dark, smooth) ────────────────────────────────────────────────
st.markdown("""
<style>
:root{
  --bg: #0f1321;
  --panel: #131a2e;
  --muted: #0d1426;
  --text: #eef1ff;
  --sub: #a6b0d6;
  --accent: #7c5cff;
  --shadow: 0 16px 40px rgba(0,0,0,.35);
  --radius: 22px;
}

#MainMenu, header[data-testid="stHeader"], footer, [data-testid="stToolbar"] { display: none !important; }

.stApp, .main, .block-container {
  background: radial-gradient(1200px 600px at 15% 10%, #151b31 0%, var(--bg) 40%, #0b1020 100%) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  color: var(--text) !important;
  box-shadow: var(--shadow);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p  { color: var(--text) !important; }

/* Floating control panel */
#floating-controls {
  position: fixed;
  top: 20px;
  left: 20px;
  background: var(--panel);
  padding: 18px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid rgba(255,255,255,.06);
  z-index: 9999;
  min-width: 240px;
}

/* Buttons */
.stButton > button {
  background: var(--accent) !important;
  color: white !important;
  border: none !important;
  border-radius: 14px !important;
  padding: 10px 16px !important;
  box-shadow: 0 10px 24px rgba(124,92,255,.35);
}

/* Cards */
.card {
  background: linear-gradient(180deg, var(--panel), var(--muted));
  border-radius: var(--radius);
  padding: 22px 24px;
  box-shadow: var(--shadow);
  border: 1px solid rgba(255,255,255,.04);
}

h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }
.small { color: var(--sub); font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar toggle logic ──────────────────────────────────────────────────────
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = True

def toggle_sidebar():
    st.session_state.sidebar_visible = not st.session_state.sidebar_visible
    st.rerun()

# ── Controls ─────────────────────────────────────────────────────────────────
if st.session_state.sidebar_visible:
    st.sidebar.header("Adjust Parameters")
    wind = st.sidebar.slider("Wind Intensity", 0.0, 100.0, 50.0)
    temp = st.sidebar.slider("Temperature (°C)", 10.0, 40.0, 27.0)
    st.sidebar.button("Hide Controls", on_click=toggle_sidebar)
else:
    st.markdown(
        """
        <div id="floating-controls">
            <p style="color:white; margin:0 0 10px 0;">Controls Hidden</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    show = st.button("Show Controls", key="showbtn")
    if show:
        toggle_sidebar()
    # Default values when hidden
    wind, temp = 50.0, 27.0

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="card" style="margin-bottom:18px; display:flex; align-items:center; justify-content:space-between;">
      <div>
        <h1 style="margin:0; letter-spacing:.3px;">Team 68</h1>
        <div class="small">Synthetic 37-bus network visualization</div>
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

# ── Data ──────────────────────────────────────────────────────────────────────
buses = pd.read_csv("data/csv/buses.csv")
connections = [(i, i+1) for i in range(1, 37)]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12.5, 8), dpi=120)
bg = "#131a2e"
accent = "#7c5cff"

fig.patch.set_facecolor(bg)
ax.set_facecolor(bg)

ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

# Draw transmission lines
for a, b in connections:
    try:
        x1, y1 = buses.loc[buses["name"] == a, ["x", "y"]].values[0]
        x2, y2 = buses.loc[buses["name"] == b, ["x", "y"]].values[0]
        ax.plot([x1, x2], [y1, y2], color="#8a93b6", linewidth=1.4, zorder=1, alpha=.9)
    except IndexError:
        continue

# Draw buses (larger, no numbers)
for _, row in buses.iterrows():
    c = accent if row["v_nom"] == 138.0 else "#53d19d"
    ax.scatter(row["x"], row["y"], color=c, s=280, edgecolors='white', linewidths=1.3, zorder=2)

# Legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='138 kV',
               markerfacecolor=accent, markeredgecolor='white', markeredgewidth=1, markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='69 kV',
               markerfacecolor='#53d19d', markeredgecolor='white', markeredgewidth=1, markersize=10),
    plt.Line2D([0], [0], color="#8a93b6", lw=2, label='Transmission Line')
]
leg = ax.legend(handles=legend_elements, loc='upper right', frameon=True)
leg.get_frame().set_facecolor("#1a2140")
leg.get_frame().set_edgecolor("none")
for text in leg.get_texts():
    text.set_color("#e9ecff")

# ── Display inside styled card ────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.pyplot(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
