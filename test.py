# test_parser.py
from utils.parse_aux import parse_aux
import pandas as pd

# Path to your uploaded file
file_path = "data/Hawaii40_20231026.AUX"

# Parse the AUX
buses, lines = parse_aux(file_path)

# Basic verification
print("\n=== BUSES ===")
print(buses.head())
print(f"Total buses: {len(buses)}")

print("\n=== LINES ===")
print(lines.head())
print(f"Total lines: {len(lines)}")

# Optional: check if IDs link correctly
bad_refs = lines[~lines["from"].isin(buses["id"]) | ~lines["to"].isin(buses["id"])]
if len(bad_refs):
    print("\n⚠️ Lines referencing unknown buses:")
    print(bad_refs)
else:
    print("\n✅ All lines reference valid buses.")