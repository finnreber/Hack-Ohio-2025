from utils.parse_aux import parse_aux
from utils.compute_stress import compute_stress
from utils.plot_map import plot_grid

import streamlit as st

st.title("🎨 Welcome to Streamlit GUI Test")

# Text input
name = st.text_input("Enter your name:")

# Color picker
color = st.color_picker("Pick your favorite color:", "#00f900")

# Button
if st.button("Greet Me"):
    st.markdown(f"### Hello, **{name}**! 👋")
    st.markdown(f"<div style='width:100px;height:100px;background-color:{color};'></div>", unsafe_allow_html=True)
