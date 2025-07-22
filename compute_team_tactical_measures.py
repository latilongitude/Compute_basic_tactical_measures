import pandas as pd
import numpy as np

from shapely.geometry import Polygon

#%% pre=processed team positional data
"""

*** An example after pre-processing provided below ***


|   Timestamp   |  Start [s]  |   ID_1_x    |   ID_1_y    |   ID_2_x    |   ID_2_y    |   ID_3_x    |   ID_4_y    |
|:-------------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|      ...      |     ...     |     ...     |     ...     |     ...     |     ...     |     ...     |     ...     |

"""

#%% calculate centroid, area, and bounds for valid coordinates

def compute_metrics(row):
    """Compute centroid, area, and bounding box from valid player positions in a single row."""
    
    # Extract player coordinates
    x_cols = [col for col in row.index if col.endswith('_x')]
    y_cols = [col for col in row.index if col.endswith('_y')]
    
    x_vals = row[x_cols].values
    y_vals = row[y_cols].values

    # Filter valid (x, y) pairs (i.e., both not NaN)
    coords = [(x, y) for x, y in zip(x_vals, y_vals) if pd.notna(x) and pd.notna(y)]
    
    if len(coords) < 3:
        raise ValueError("Not enough valid coordinates to form a polygon.")
    
    # Create convex hull and extract geometry
    polygon = Polygon(coords).convex_hull
    area = polygon.area
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)

    # Compute centroid excluding repeated last point
    exterior_coords = list(polygon.exterior.coords)[:-1]
    centroid_x = np.mean([pt[0] for pt in exterior_coords])
    centroid_y = np.mean([pt[1] for pt in exterior_coords])

    return centroid_x, centroid_y, area, *bounds


#%% read data

# Read the dataset (insert the actual file path below)
data_team = pd.read_csv("Your_File_Path.csv")

# Drop any rows with missing values
data_team = data_team.dropna()

# Reset the index after dropping rows
data_team = data_team.reset_index(drop=True)

#%% compute team tactical measures

# DataFrame to store results
measures = pd.DataFrame(columns=["cen_x", "cen_y", "surface area", "minx", "miny", "maxx", "maxy"])

# Process each row of the dataset
for idx, row in data_team.iterrows():
    try:
        metrics = compute_metrics(row)
        measures.loc[len(measures)] = metrics
    except ValueError as e:
        print(f"Row {idx}: {e}")

print("Metrics computation DONE.")

# Add length, width, and length-per-width ratio
measures["length"] = measures["maxx"] - measures["minx"]
measures["width"] = measures["maxy"] - measures["miny"]
measures["LpW"] = measures["length"] / measures["width"]

# Output
print(measures)