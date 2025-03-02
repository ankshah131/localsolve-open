import streamlit as st
import folium
import pandas as pd
import requests
import geopandas as gpd
from io import BytesIO
from branca.colormap import LinearColormap
from streamlit_folium import folium_static

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

class InvasivesMap:
    def __init__(self):
        self.TILE_BURN_SEVERITY = "https://storage.googleapis.com/localsolve_assets/dNBR_Classified_Colored_Tiles_High_Zoom/{z}/{x}/{y}.png"
        self.VEGETATION_GEOJSON_URL = "https://storage.googleapis.com/localsolve_assets/Vegetationwithburn_mode.geojson"
        self.INVASIVES_GEOJSON_URL = "https://storage.googleapis.com/localsolve_assets/la_wildfires_jan_2025/calveg_invasive_species.geojson"  # Replace with actual URL

        self.mode_categories = {
            0: "NA",
            1: "High Severity",
            2: "Moderate-high Severity",
            3: "Moderate-low Severity",
            4: "Low Severity",
            5: "Unburned",
            6: "Enhanced Regrowth, Low",
            7: "Enhanced Regrowth, High"
        }
        
        self.bounding_box = [
            [34.01190896623858, -118.71175096860182],
            [34.20804709919758, -118.33340929379713]
        ]

def load_geojson_data(self, url):
    """Generic function to load GeoJSON data from a URL and handle datetime issues."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        gdf = gpd.read_file(BytesIO(response.content))
        gdf = gdf.to_crs(epsg=4326)

        # Convert ALL datetime columns to string to avoid JSON serialization errors
        for col in gdf.columns:
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                gdf[col] = gdf[col].astype(str)  # Convert timestamp to string

        return gdf
    except Exception as e:
        st.error(f"Error loading data from {url}: {str(e)}")
        return None


    def create_colormap(self):
        return LinearColormap(
            [
                "#a41fd6", "#ff641b", "#ffaf38", "#fff70b", 
                "#0ae042", "#acbe4d", "#7a8737", "#ffffff"
            ],
            index=[1, 2, 3, 4, 5, 6, 7], vmin=1, vmax=7,
            caption="Burn Severity"
        )

    def create_map(self):
        try:
            m = folium.Map(
                location=[34.21748, -118.1339],
                zoom_start=14,
                tiles="cartodbpositron",
                min_zoom=6,
                max_zoom=14,
                max_bounds=True
            )
            
            m.fit_bounds(self.bounding_box)
            
            folium.TileLayer(
                tiles=self.TILE_BURN_SEVERITY,
                attr="Sentinel-2 Burn Severity",
                name="Burn Severity",
                overlay=True
            ).add_to(m)
            
            # Load and add vegetation burn severity layer
            # gdf_vegetation = self.load_geojson_data(self.VEGETATION_GEOJSON_URL, mode_field="mode")
            # if gdf_vegetation is not None:
            #     colormap = self.create_colormap()
                
            #     folium.GeoJson(
            #         gdf_vegetation,
            #         name="Vegetation Burn Severity",
            #         style_function=lambda feature: {
            #             "fillColor": colormap(feature["properties"].get("mode", 1)),
            #             "color": "black",
            #             "weight": 0.7,
            #             "fillOpacity": 0.6
            #         },
            #         tooltip=folium.GeoJsonTooltip(
            #             fields=["Class_Cnam", "Class_Snam", "burn_severity_category"],
            #             aliases=["Common Name", "Scientific Name", "Burn Severity Category"]
            #         )
            #     ).add_to(m)
                
            #     m.add_child(colormap)

            # Load and add invasive species layer
            gdf_invasives = self.load_geojson_data(self.INVASIVES_GEOJSON_URL)
            if gdf_invasives is not None:
                folium.GeoJson(
                    gdf_invasives,
                    name="Invasive Species",
                    style_function=lambda feature: {
                        "fillColor": "#FF0000",  # Red for invasives
                        "color": "#990000",
                        "weight": 0.8,
                        "fillOpacity": 0.6
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["ACCEPTED_C", "ACCEPTED_S", "LAST_UPDAT"],
                        aliases=["Common Name", "Scientific Name", "Date of Last Update"]
                    )
                ).add_to(m)

            folium.LayerControl().add_to(m)
            
            return m
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            return None

    def display(self):
        st.title("Invasive Species Map for the Eaton Fire")
        
        col1, col2 = st.columns([2, 1])  # Creating two columns, with col1 taking 2/3 space
    
        with col1:
            with st.spinner("Loading map... This may take a few moments..."):
                m = self.create_map()
                if m is not None:
                    folium_static(m, width=1000, height=600)
    
        with col2:
            st.subheader("How Burn Severity is Measured")
            st.write(
                "Burn severity is assessed using Sentinel-2 satellite imagery by "
                "calculating the differenced Normalized Burn Ratio (dNBR), which compares "
                "pre-fire and post-fire conditions. The dNBR is derived from the near-infrared "
                "(NIR) and shortwave infrared (SWIR) bands of Sentinel-2, where higher values "
                "indicate severe burns and lower values represent healthy vegetation or regrowth. "
            )

            st.subheader("Invasive Species Layer")
            st.write(
                "The invasive species layer highlights areas where non-native species have been detected. "
                "These species can disrupt local ecosystems by outcompeting native plants, altering fire regimes, "
                "and affecting soil composition. Monitoring and managing invasive species is crucial for ecological restoration."
            )


def main():
    st.set_page_config(layout="wide")
    analysis = InvasivesMap()
    analysis.display()

if __name__ == "__main__":
    main()
