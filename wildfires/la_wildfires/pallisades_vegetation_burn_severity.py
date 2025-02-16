import geopandas as gpd
import folium
from io import BytesIO
from branca.colormap import LinearColormap
import requests

# Public GeoJSON URL
GEOJSON_URL = "https://storage.googleapis.com/localsolve_assets/Vegetationwithburn_mode.geojson"

# Fetch GeoJSON data
response = requests.get(GEOJSON_URL)
if response.status_code == 200:
    geojson_data = response.content
else:
    raise Exception("Failed to fetch GeoJSON data")

# Read as GeoDataFrame
gdf = gpd.read_file(BytesIO(geojson_data))

# Ensure CRS is in EPSG:4326
gdf = gdf.to_crs(epsg=4326)

# Round off "mode" column to the nearest integer
gdf["mode"] = gdf["mode"].round().astype(int)

# Define mode-to-category mapping
mode_categories = {
    0: "NA",
    1: "High Severity",
    2: "Moderate-high Severity",
    3: "Moderate-low Severity",
    4: "Low Severity",
    5: "Unburned",
    6: "Enhanced Regrowth, Low",
    7: "Enhanced Regrowth, High"
}

# Add a new column with descriptive burn severity categories
gdf["burn_severity_category"] = gdf["mode"].map(mode_categories)

# Define a custom colormap for "mode" values
colormap = LinearColormap(
    [
        "#a41fd6", "#ff641b", "#ffaf38", "#fff70b", 
        "#0ae042", "#acbe4d", "#7a8737", "#ffffff"
    ], 
    index=[1, 2, 3, 4, 5, 6, 7], vmin=1, vmax=7
)

# Define burn severity tile layer
TILE_BURN_SEVERITY = "https://storage.googleapis.com/localsolve_assets/dNBR_Classified_Colored_Tiles_High_Zoom/{z}/{x}/{y}.png"

# Define bounding box for map extent
bounding_box = [
    [34.01190896623858, -118.71175096860182],  # Bottom-left (lat, lon)
    [34.20804709919758, -118.33340929379713]   # Top-right (lat, lon)
]

# Create a Folium map centered on Los Angeles with extent restrictions
m = folium.Map(
    location=[34.19429652892988, -118.45538398388315], 
    zoom_start=11, 
    tiles="cartodbpositron",
    min_zoom=6,
    max_zoom=14,
    max_bounds=True
)

# Fit the map to the bounding box
m.fit_bounds(bounding_box)

# Add burn severity layer
folium.TileLayer(
    tiles=TILE_BURN_SEVERITY,
    attr="Sentinel-2 Burn Severity",
    name="Burn Severity",
    overlay=True
).add_to(m)

# Create a feature group for vegetation polygons
polygon_layer = folium.FeatureGroup(name="Vegetation Burn Mode", overlay=True).add_to(m)

# Add polygons with fill color based on "mode" values
folium.GeoJson(
    gdf,
    name="Vegetation Polygons",
    style_function=lambda feature: {
        "fillColor": colormap(feature["properties"].get("mode", 1)),  # Set fill color based on mode value
        "color": "black",  # Outline color
        "weight": 0.7,
        "fillOpacity": 0.6  # Adjust transparency
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["Class_Cnam", "Class_Snam", "mode", "burn_severity_category"],  
        aliases=["Common Name", "Scientific Name", "Burn Severity Mode", "Burn Severity Category"]
    )
).add_to(polygon_layer)

# Add colormap legend
m.add_child(colormap)

# Add layer control to toggle between layers
folium.LayerControl().add_to(m)

# Display the map
m
