import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# Title
st.title("Hawaii Synthetic Grid – 37 Buses")

# Create a synthetic graph
G = nx.Graph()

# Add nodes (buses)
for i in range(1, 38):
    G.add_node(i)

# Add edges (connections between buses)
edges = [
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),
    (6, 7), (7, 8), (8, 9), (9, 10), (10, 11),
    # Add more edges based on actual topology or synthetic logic
]
G.add_edges_from(edges)

# Draw the graph
fig, ax = plt.subplots()
nx.draw(G, with_labels=True, node_color='skyblue', edge_color='gray', node_size=500, ax=ax)
st.pyplot(fig)

# Slide selector
slide = st.radio("Select Slide", ["Weather", "Temperature"])

if slide == "Weather":
    st.subheader("🌤️ Weather Conditions")
    st.write("Today's forecast for Oahu includes scattered clouds, light wind, and moderate humidity.")
    st.image("https://example.com/weather_icon.png")  # Replace with actual image URL or local file

elif slide == "Temperature":
    st.subheader("🌡️ Temperature Overview")
    st.write("Average temperature across the grid is 27°C with slight variations near coastal nodes.")
    st.line_chart([26, 27, 28, 27, 26])  # Sample temperature data
