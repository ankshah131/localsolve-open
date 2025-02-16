import folium
import requests

def fetch_geojson(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Initialize the map centered around Los Angeles
m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)

# Define GeoJSON URLs and styles
geojson_configs = [
    {"url": "https://storage.googleapis.com/localsolve_assets/la_infrastructure/Burned_or_damaged_clinics.geojson", 
     "layer_name": "Burned or Damaged Clinics", 
     "style": {"fillColor": "red", "color": "black", "weight": 1, "fillOpacity": 0.6},
     "tooltip_fields": ["name", "healthcare"]},
    {"url": "https://storage.googleapis.com/localsolve_assets/la_infrastructure/healthcare_hospital_los%20Angeles.geojson", 
     "layer_name": "Healthcare Hospitals", 
     "style": {"fillColor": "blue", "color": "black", "weight": 1, "fillOpacity": 0.6},
     "tooltip_fields": ["name", "amenity"]}
]

# Add each GeoJSON layer to the map
for config in geojson_configs:
    geojson_data = fetch_geojson(config["url"])
    if geojson_data:
        geojson_layer = folium.FeatureGroup(name=config["layer_name"], overlay=True).add_to(m)
        folium.GeoJson(
            geojson_data,
            name=config["layer_name"],
            style_function=lambda feature, style=config["style"]: style,
            tooltip=folium.GeoJsonTooltip(fields=config["tooltip_fields"], aliases=config["tooltip_fields"])
        ).add_to(geojson_layer)

# Add layer control
folium.LayerControl().add_to(m)
