import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(page_title="Hawaii Grid", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Grey Background ---
st.markdown("""
    <style>
        body, .main, .block-container {
            background-color: #e0e0e0 !important;
        }
        .stPlotlyChart, .stImage, .stMarkdown {
            background-color: #e0e0e0 !important;
            box-shadow: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Top Header ---
st.markdown("<h1 style='text-align: center; color: black;'>Team 68</h1>", unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.header("Adjust Parameters")
wind = st.sidebar.slider("Wind Intensity", 0.0, 100.0, 50.0)
temp = st.sidebar.slider("Temperature (°C)", 10.0, 40.0, 27.0)

# --- Load Bus Data ---
buses = pd.read_csv("data/buses.csv")

# --- Placeholder Connections (until actual mapping is provided) ---
# This assumes L0 connects bus 1 to 2, L1 connects 2 to 3, etc.
# You can replace this with actual mappings once available
connections = [(i, i+1) for i in range(1, 37)]  # 36 lines connecting sequential buses

# --- Plot Setup ---
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_facecolor("#e0e0e0")
ax.set_title("Hawaii Synthetic Grid – 37 Buses", fontsize=16)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# --- Plot Connections ---
for a, b in connections:
    try:
        x1, y1 = buses.loc[buses["name"] == a, ["x", "y"]].values[0]
        x2, y2 = buses.loc[buses["name"] == b, ["x", "y"]].values[0]
        ax.plot([x1, x2], [y1, y2], color="gray", linewidth=1, zorder=1)
    except IndexError:
        continue  # skip if bus not found

# --- Plot Buses ---
for _, row in buses.iterrows():
    color = "black" if row["v_nom"] == 138.0 else "green"
    ax.scatter(row["x"], row["y"], color=color, s=120, edgecolors='white', zorder=2)
    ax.text(row["x"], row["y"], str(int(row["name"])), fontsize=8, ha='center', va='center', color='white')

# --- Legend ---
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='138 kV', markerfacecolor='black', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='69 kV', markerfacecolor='green', markersize=10),
    plt.Line2D([0], [0], color='gray', lw=2, label='Transmission Line')
]
ax.legend(handles=legend_elements, loc='upper right')

# --- Display Plot ---
st.pyplot(fig)
 
