---
title:  "Unlocking BGS Data with H3: Using Hexagonal Grids to Democratize Geospatial Data"
author: Edd Lewis
categories:
  - Software Engineering
tags:
  - python
  - h3
  - products
  - data
---

# Unlocking BGS Data with H3: Using Hexagonal Grids to Democratize Geospatial Data

Geospatial data is often complex, high-resolution, and notoriously difficult to aggregate and summarize at scale. At the British Geological Survey (BGS), we hold vast amounts of premium, highly detailed geological data. While this data is invaluable for site-specific engineering and environmental assessments, there is also a massive demand for national-scale, open-access screening tools.

To bridge this gap, BGS is leveraging H3, a Hexagonal Discrete Global Grid System (DGGS), to transform premium, high-resolution datasets into accessible, open-data summaries.

In this post, we'll introduce H3, explore why it's such a powerful tool for geospatial analysis, and dive into how we use Python to aggregate two of our major datasets: Mining Hazards and the Superficial Deposit Thickness Model (SDTM).

# What is H3 and Why is it Good?

Originally developed by Uber to optimize ride-sharing dispatch, H3 is a geospatial indexing system that partitions the globe into hexagonal cells.

But why hexagons instead of the traditional square grids (like raster pixels or bounding boxes)?

1. Uniform Neighbors: Unlike squares, where diagonal neighbors are further away than adjacent ones, every neighbor of a hexagon is exactly the same distance from its center. This makes spatial algorithms, smoothing, and traversal much more efficient and mathematically consistent.

2. Low Area Distortion: H3 utilizes an icosahedron projection, resulting in cells that maintain relatively consistent areas across the globe.

3. Hierarchical Scaling: H3 supports 16 resolutions. You can easily aggregate data from smaller hexagons into larger parent hexagons, making it perfect for zooming in and out of datasets.

4. Fast Aggregation: H3 indexes are represented as simple 64-bit integers or strings. Finding point-in-polygon relationships becomes a highly optimized string or integer matching exercise, rather than a heavy geographic geometry calculation.

# What can you do with H3?

Organizations across the world use H3 for:

- Machine Learning: Standardizing diverse spatial data (points, lines, polygons) into a consistent grid of features for predictive modeling.

- Large-Scale Visualization: Rendering millions of data points on web maps dynamically by grouping them into hex bins.

- Privacy & Data Aggregation: Obfuscating exact point locations (like user data or proprietary business intelligence) while retaining regional trends.

At BGS, we heavily rely on this third use case: summarizing premium data to create **Open Government Licence (OGL)** screening tools, sample  datasets and maps for public consumption.

# The BGS Use Case: Creating Open Data Products

BGS maintains highly detailed, licenced datasets. However, we want to provide the public, researchers, and regional planners with broad-scale overviews of geological trends.

By aggregating our premium vector and raster data into **H3 Resolution 7** hexagons (which have an edge length of approximately 1.2km), we can publish generalized screening tools. These open datasets allow users to identify regional trending and hazards to inform where more detailed investigations are needed, without giving away the site-specific commercial data.

Let's look at two practical examples of how we achieve this using Python, `geopandas`, and `h3-py`.

# Use Case 1: Aggregating Mining Hazards

Our BGS Mining Hazard (not including coal) dataset provides detailed assessments of ground instability caused by historic non-coal mineral workings. To create an open version, we needed to summarize the hazard class for each H3 cell.

The Methodology:

1. **Spatial Overlay**: We intersect our detailed hazard polygons with the H3 grid.

2. **Metric Calculation (Max Class)**: We determine the highest hazard class (Lexicographically A-E) found within any part of the hexagon.

3. **Classification**: We map these raw classes into user-friendly, less specific (than the premium product) risk categories: "Low" (A/B), "Moderate" (C), and "Significant" (D/E).

Here is how we handle the intersection and aggregation in Python:

```python
import geopandas as gpd
import pandas as pd

# 1. Perform Spatial Intersection between premium hazard polygons and H3 grid
overlay = gpd.overlay(hazard_gdf, hex_grid_gdf, how="intersection", keep_geom_type=True)

# 2. Convert the 'CLASS' column to an ordered categorical type
custom_order = ["UNCLASSIFIED", "A", "B", "C", "D", "E"]
overlay["CLASS"] = pd.Categorical(overlay["CLASS"], categories=custom_order, ordered=True)

# 3. Calculate the Max Class per Hexagon (H3_IX)
grouped = overlay.groupby("H3_IX")
max_class_df = grouped["CLASS"].max().reset_index(name="MAX_CLASS")

# 4. Map to simplified risk categories
def get_risk_class(val):
    if val in ["A", "B"]: return "Low"
    if val == "C": return "Moderate"
    if val in ["D", "E"]: return "Significant"
    return "Unclassified"

max_class_df["RISK_CATEGORY"] = max_class_df["MAX_CLASS"].apply(get_risk_class)
```

This ensures that if even a small sliver of a "Significant" (Class E) hazard intersects a 1.2km hexagon, the entire hexagon alerts the user to the potential hazard, serving as a perfect regional screening tool.

# Use Case 2: Superficial Deposit Thickness Model (SDTM)

The SDTM provides a gridded model of sediment thickness (depth to geological rockhead) across Great Britain. Understanding this transition zone is vital for civil engineers and hydrogeologists.

To build the Open SDTM dataset, we calculate robust summary statistics for each H3 cell. We extract the **Maximum Depth**, the **Coverage Percentage** of the cell, the **Borehole Count** intersecting the cell, and crucially, the **Weighted Mean** thickness.

Calculating a weighted mean is essential. If a deep geological basin only clips the edge of a hexagon, a standard average would over-represent that depth. We weight the depth by the physical area of the intersection.

```python
# Perform the spatial overlay
overlay = gpd.overlay(sdtm_gdf, hex_grid_gdf, how="intersection", keep_geom_type=True)
overlay["INTERSECTION_AREA_M2"] = overlay.geometry.area

grouped = overlay.groupby("H3_IX")

# Metric 1: Max Depth
max_bstm = grouped["ODM"].max().rename("ODM_MAX").round(0).astype(int)

# Metric 2: Area-Weighted Mean Depth
def weighted_mean(df):
    total_area = df["INTERSECTION_AREA_M2"].sum()
    if total_area == 0:
        return 0
    # Multiply depth by intersection area, sum, and divide by total intersection area
    return (df["ODM"] * df["INTERSECTION_AREA_M2"]).sum() / total_area

mean_bstm = grouped.apply(weighted_mean, include_groups=False).rename("ODM_MEAN").round(0).astype(int)
```

By wrapping this data in an H3 framework, researchers can easily join this thickness data with other H3-indexed datasets (like environmental factors or infrastructure grids) purely by joining on the H3_IX string index, bypassing costly spatial joins altogether.

# Conclusion

The adoption of the H3 DGGS at the British Geological Survey represents a major step forward in how we handle, aggregate, and distribute spatial data.

By applying spatial intersections and custom aggregations — like the lexicographical 'Max Class' for hazards or 'Weighted Means' for geological thickness — we can successfully distill highly complex, licenced datasets into accessible Open Government Licence formats.

These generalized hex grids empower users to conduct desktop studies, spot national trends, and make informed decisions on where to commission detailed, site-specific investigations. As geospatial data continues to grow in size and complexity, systems like H3 will be critical in making sense of the noise.

*Want to dive deeper into our open datasets? Visit the BGS Datasets page to explore the SDTM and Mining Hazard H3 products.*