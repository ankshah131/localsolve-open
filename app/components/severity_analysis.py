import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# Define burn severity classes with corresponding colors
BURN_SEVERITY_CLASSES = {
    "Enhanced Regrowth, High": "#7a8737",
    "Enhanced Regrowth, Low": "#acbe4d",
    "Unburned": "#0ae042",
    "Low Severity": "#fff70b",
    "Moderate-low Severity": "#ffaf38",
    "Moderate-high Severity": "#ff641b",
    "High Severity": "#a41fd6",
    "NA": "#ffffff"
}

class SeverityAnalysis:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.TILE_URL_PRE_BURN = "https://storage.googleapis.com/localsolve_assets/S2_LA_Pre_Burn_High_Zoom/{z}/{x}/{y}.png"
        self.TILE_URL_POST_BURN = "https://storage.googleapis.com/localsolve_assets/S2_LA_Post_Burn_High_Zoom/{z}/{x}/{y}.png"
        self.TILE_BURN_SEVERITY = "https://storage.googleapis.com/localsolve_assets/dNBR_Classified_Colored_Tiles_High_Zoom/{z}/{x}/{y}.png"
        self.GEOJSON_URL = "https://storage.googleapis.com/localsolve_assets/merged_LA_fires_2025.geojson"


        

    def create_map(self):
        # Create a Folium map centered on Los Angeles
        m = folium.Map(location=[34.18716861471849, -118.32657647829909], 
                      zoom_start=11, min_zoom=6,max_zoom=14, max_bounds=True,
                      tiles="cartodbpositron")
        
        # Add pre-burn layer
        folium.TileLayer(
            tiles=self.TILE_URL_PRE_BURN,
            attr="Sentinel-2 Pre-Burn Imagery",
            name="Pre-Burn",
            overlay=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles=self.TILE_URL_POST_BURN,
            attr="Sentinel-2 Post-Burn Imagery",
            name="Post-Burn",
            overlay=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles=self.TILE_BURN_SEVERITY,
            attr="Sentinel-2 Burn Severity",
            name="Burn Severity",
            overlay=True
        ).add_to(m)
        
        
        # Fetch GeoJSON data
        response = requests.get(self.GEOJSON_URL)
        if response.status_code == 200:
            geojson_data = response.json()
        
            # Create a FeatureGroup for the polygons
            polygon_layer = folium.FeatureGroup(name="Fire Perimeters", overlay=True).add_to(m)
        
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
                    fields=["mission", "area_acres", "source"],  # Customize tooltip fields
                    aliases=["Mission Name", "Area (acres)", "Source"]
                )
            ).add_to(polygon_layer)
        
        # Add layer control to toggle between layers
        folium.LayerControl().add_to(m)
        
        return m

    def create_legend(self):
        """Create and display the burn severity legend."""
        # Add CSS to style the legend
        st.markdown("""
            <style>
            .legend-item {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }
            .color-box {
                width: 20px;
                height: 20px;
                margin-right: 10px;
                border: 1px solid #ccc;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.subheader("Burn Severity Legend")
        # Create legend items
        for label, color in BURN_SEVERITY_CLASSES.items():
            st.markdown(
                f'<div class="legend-item">'
                f'<div class="color-box" style="background-color: {color};"></div>'
                f'<span>{label}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    # def display(self):
    #     st.title("LA Fires Burn Severity Analysis")
        
    #     # Create columns for the layout
    #     col1, col2 = st.columns([3, 1])
        
    #     with col1:
    #         st.subheader("Interactive Fire Map")
    #         # Create the map and display it using st_folium
    #         m = self.create_map()
    #         st_folium(m, width=1000, height=600)
            
    #     with col2:
    #         st.subheader("Map Controls")
    #         st.write("""
    #         Use the layer control in the top right of the map to toggle between:
    #         - Pre-Burn Imagery
    #         - Post-Burn Imagery
    #         - Burn Severity
    #         - Fire Perimeters
    #         """)
            
    #         st.info("Click on fire perimeters to view details about each fire mission.")
            
    #         # Add the legend below the map controls
    #         self.create_legend()

    def display(self):
        st.title("LA Fires Burn Severity Analysis")

        # Create columns for the layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Interactive Fire Map")
            m = self.create_map()
            map_data = st_folium(m, width=1000, height=600)

            # Show clicked coordinates
            if map_data and map_data.get("last_clicked"):
                lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                st.info(f"Clicked Coordinates: Latitude {lat}, Longitude {lon}")
            
        with col2:
            st.subheader("How to Use the Map")
            st.write("""
            - Click on the **layer control (top right of the map)** to switch between:
              - Pre-Burn Imagery
              - Post-Burn Imagery
              - Burn Severity
              - Fire Perimeters
            - **Hover over fire perimeters** to see fire details.
            - **Click anywhere on the map** to get the latitude and longitude.
            """)

            st.info("Click on fire perimeters to view details about each fire mission.")

            # Add the legend below the map controls
            self.create_legend()


def main():
    st.set_page_config(layout="wide")
    analysis = SeverityAnalysis()
    analysis.display()

if __name__ == "__main__":
    main()
