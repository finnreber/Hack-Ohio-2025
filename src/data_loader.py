import pandas as pd
import geopandas as gpd

def load_data():
    lines = pd.read_csv("data/csv/lines.csv")
    flows = pd.read_csv("data/csv/line_flows_nominal.csv")
    buses = pd.read_csv("data/csv/buses.csv")
    g_lines = gpd.read_file("data/gis/oneline_lines.geojson")
    g_buses = gpd.read_file("data/gis/oneline_busses.geojson")
    return lines, flows, buses, g_lines, g_buses