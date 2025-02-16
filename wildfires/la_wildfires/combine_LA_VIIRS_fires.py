import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Define file paths
file_paths = [
    "/content/fire_nrt_J1V-C2_578646.csv",
    "/content/fire_nrt_J2V-C2_578647.csv",
    "/content/fire_nrt_SV-C2_578648.csv"
]

# Read and concatenate the files
df_list = [pd.read_csv(file) for file in file_paths]
df_combined = pd.concat(df_list, ignore_index=True)

# Save the combined dataset
df_combined.to_csv("la_january_2025_fire_hotspots_combined.csv", index=False)

# Print confirmation
print("CSV files have been successfully combined and saved as fire_hotspots_combined.csv.")

# Remove rows where confidence is 'l'
df = df_combined[df_combined['confidence'] != 'l']

# Convert the CSV into a GeoDataFrame
gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")

# Load the GeoJSON file with fire perimeters
geojson_file = "/content/merged_LA_2025_fires.geojson"  # Replace with your file path
gdf_polygons = gpd.read_file(geojson_file)

# Ensure both layers are in the same coordinate reference system (CRS)
gdf_polygons = gdf_polygons.to_crs(gdf_points.crs)

# Perform a spatial join to keep only fire points within the fire perimeters
filtered_points = gpd.sjoin(gdf_points, gdf_polygons, predicate="within")

# Save the filtered data to a new CSV file
filtered_points.drop(columns=["geometry"]).to_csv("filtered_la_january_2025_fire_hotspots_combined.csv", index=False)

print("Filtered fire points saved to 'filtered_la_january_2025_fire_hotspots_combined.csv'")
