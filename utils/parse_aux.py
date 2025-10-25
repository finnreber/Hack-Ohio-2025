import re
import pandas as pd

def parse_aux(file_path: str):
    """Parse PowerWorld .AUX file and extract substations (buses) and branches (lines + transformers)."""
    with open(file_path, "r", errors="ignore") as f:
        text = f.read()

    # --- Extract Substations (Buses) ---
    bus_pattern = re.compile(
        r'\s*(\d+)\s+"([^"]+)"\s+"[^"]*"\s+([-\d.]+)\s+([-\d.]+)',
        re.MULTILINE
    )
    buses = pd.DataFrame(bus_pattern.findall(text), columns=["id", "name", "lat", "lon"])
    buses["id"] = buses["id"].astype(int)
    buses["lat"] = buses["lat"].astype(float)
    buses["lon"] = buses["lon"].astype(float)

    # --- Helper: Extract branch sections (Line + Transformer) ---
    branch_blocks = re.findall(r'Branch\s*\(.*?\)\s*\{(.*?)\}', text, re.DOTALL | re.IGNORECASE)
    all_branches = []
    for block in branch_blocks:
        # Match patterns like:
        #    1     5 "1"  "Line" ...
        # or  1     2 "1"  "Transformer" ...
        branch_pattern = re.compile(
            r'\s*(\d+)\s+(\d+)\s+"[^"]+"\s+"([^"]+)"',  # BusFrom, BusTo, Type ("Line" or "Transformer")
            re.MULTILINE
        )
        for frm, to, typ in branch_pattern.findall(block):
            all_branches.append((int(frm), int(to), typ))

    lines = pd.DataFrame(all_branches, columns=["from", "to", "type"])

    # --- Filter out invalid or duplicate rows ---
    lines.drop_duplicates(inplace=True)
    lines = lines[(lines["from"] != lines["to"])]

    # --- Sanity check: find missing buses ---
    known_buses = set(buses["id"].astype(int))
    invalid_lines = lines[~lines["from"].isin(known_buses) | ~lines["to"].isin(known_buses)]

    return buses, lines
