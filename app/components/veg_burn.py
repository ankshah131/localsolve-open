import streamlit as st
import folium
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

class VegBurn:
    def __init__(self):
        self.TILE_BURN_SEVERITY = "https://storage.googleapis.com/localsolve_assets/dNBR_Classified_Colored_Tiles_High_Zoom/{z}/{x}/{y}.png"
        self.VEGETATION_GEOJSON_URL = "https://storage.googleapis.com/localsolve_assets/Vegetationwithburn_mode.geojson"
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

    def load_vegetation_data(self):
        try:
            response = requests.get(self.VEGETATION_GEOJSON_URL)
            response.raise_for_status()
            
            gdf = gpd.read_file(BytesIO(response.content))
            gdf = gdf.to_crs(epsg=4326)
            
            gdf["mode"] = gdf["mode"].round().astype(int)
            gdf["burn_severity_category"] = gdf["mode"].map(self.mode_categories)
            
            return gdf
        except Exception as e:
            st.error(f"Error loading vegetation data: {str(e)}")
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
                location=[34.07, -118.58],
                zoom_start=15,
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
            
            gdf = self.load_vegetation_data()
            if gdf is not None:
                colormap = self.create_colormap()
                
                folium.GeoJson(
                    gdf,
                    name="Vegetation Polygons",
                    style_function=lambda feature: {
                        "fillColor": colormap(feature["properties"].get("mode", 1)),
                        "color": "black",
                        "weight": 0.7,
                        "fillOpacity": 0.6
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["Class_Cnam", "Class_Snam", "mode", "burn_severity_category"],
                        aliases=["Common Name", "Scientific Name", "Burn Severity Mode", "Burn Severity Category"]
                    )
                ).add_to(m)
                
                m.add_child(colormap)
            
            folium.LayerControl().add_to(m)
            
            return m
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            return None

    # def display(self):
    #     st.title("Vegetation Burn Severity")
        
    #     with st.spinner("Loading map... This may take a few moments..."):
    #         m = self.create_map()
    #         if m is not None:
    #             folium_static(m, width=1000, height=600)

    def display(self):
        st.title("Vegetation Burn Severity")
        
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
                "To summarize burn impact at a landscape scale, we used the National Park Service VMI "
                "vegetation polygons and calculated the mode (most common) burn severity category "
                "within each polygon. This helps in understanding the dominant fire effects on different "
                "vegetation types."
            )


def main():
    st.set_page_config(layout="wide")
    analysis = VegBurn()
    analysis.display()

if __name__ == "__main__":
    main()
