import streamlit as st
import folium
import requests
from streamlit_folium import st_folium  # Add this import

class SeverityAnalysis:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.TILE_URL_PRE_BURN = "https://storage.googleapis.com/localsolve_assets/S2_LA_Pre_Burn/{z}/{x}/{y}.png"
        self.TILE_URL_POST_BURN = "https://storage.googleapis.com/localsolve_assets/S2_LA_Burned_Area/{z}/{x}/{y}.png"
        self.TILE_BURN_SEVERITY = "https://storage.googleapis.com/localsolve_assets/dNBR_Classified_Colored_Tiles/{z}/{x}/{y}.png"
        self.GEOJSON_URL = "https://storage.googleapis.com/localsolve_assets/merged_LA_fires_2025.geojson"

    def create_map(self):
        # Create a Folium map centered on Los Angeles
        m = folium.Map(location=[34.0486, -118.5267], 
                      zoom_start=14, 
                      tiles="cartodbpositron")
        
        # Add pre-burn layer
        folium.TileLayer(
            tiles=self.TILE_URL_PRE_BURN,
            attr="Sentinel-2 Pre-Burn Imagery",
            name="Pre-Burn",
            overlay=True
        ).add_to(m)
        
        # Add post-burn layer
        folium.TileLayer(
            tiles=self.TILE_URL_POST_BURN,
            attr="Sentinel-2 Post-Burn Imagery",
            name="Post-Burn",
            overlay=True
        ).add_to(m)
        
        # Add burn severity layer
        folium.TileLayer(
            tiles=self.TILE_BURN_SEVERITY,
            attr="Sentinel-2 Burn Severity",
            name="Burn Severity",
            overlay=True
        ).add_to(m)
        
        # Fetch and add GeoJSON data
        try:
            response = requests.get(self.GEOJSON_URL)
            if response.status_code == 200:
                geojson_data = response.json()
                
                # Create a FeatureGroup for the polygons
                polygon_layer = folium.FeatureGroup(
                    name="Fire Perimeters", 
                    overlay=True
                ).add_to(m)
                
                # Add GeoJSON layer
                folium.GeoJson(
                    geojson_data,
                    name="Fire Perimeters",
                    style_function=lambda feature: {
                        "fillColor": "red",
                        "color": "black",
                        "weight": 1,
                        "fillOpacity": 0.4
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["mission", "area_acres", "source"],
                        aliases=["Mission Name", "Area (acres)", "Source"]
                    )
                ).add_to(polygon_layer)
        except Exception as e:
            st.error(f"Error loading GeoJSON data: {str(e)}")
            
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m

    def display(self):
        st.title("LA Fires Burn Severity Analysis")
        
        # Create columns for the layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Interactive Fire Map")
            # Create the map and display it using st_folium
            m = self.create_map()
            st_folium(m, width=800, height=600)
            
        with col2:
            st.subheader("Map Controls")
            st.write("""
            Use the layer control in the top right of the map to toggle between:
            - Pre-Burn Imagery
            - Post-Burn Imagery
            - Burn Severity
            - Fire Perimeters
            """)
            
            st.info("Click on fire perimeters to view details about each fire mission.")

# Main app
def main():
    st.set_page_config(layout="wide")
    analysis = SeverityAnalysis()
    analysis.display()

if __name__ == "__main__":
    main()




