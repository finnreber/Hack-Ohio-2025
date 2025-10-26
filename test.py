import pandas as pd

# Load your actual files
buses = pd.read_csv("data/csv/buses.csv")
lines = pd.read_csv("data/csv/lines.csv")

print("=== BUSES ===")
print(buses.head())

print("\n=== LINES ===")
print(lines.head())

print("\nColumns in buses:", list(buses.columns))
print("Columns in lines:", list(lines.columns))