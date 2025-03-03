import streamlit as st
import folium
import pandas as pd
import requests
import geopandas as gpd
from io import BytesIO
from PIL import Image
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
                location=[34.21464, -118.0666],
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
            

            # # Load and add invasive species layer
            # gdf_invasives = self.load_geojson_data(self.INVASIVES_GEOJSON_URL)
            # if gdf_invasives is not None:
            #     folium.GeoJson(
            #         gdf_invasives,
            #         name="Invasive Species",
            #         style_function=lambda feature: {
            #             "fillColor": "#FF0000",  # Red for invasives
            #             "color": "#990000",
            #             "weight": 0.8,
            #             "fillOpacity": 0.6
            #         },
            #         tooltip=folium.GeoJsonTooltip(
            #             fields=["ACCEPTED_C", "ACCEPTED_S", "LAST_UPDAT"],
            #             aliases=["Common Name", "Scientific Name", "Date Last Updated"]
            #         )
            #     ).add_to(m)

            # folium.LayerControl().add_to(m)

            # Load and add invasive species layer
            gdf_invasives = self.load_geojson_data(self.INVASIVES_GEOJSON_URL)
            if gdf_invasives is not None:
                # Add a new column "Source" with the fixed value "CALVEG"
                gdf_invasives["Source"] = "CALVEG"
            
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
                        fields=["ACCEPTED_C", "ACCEPTED_S", "LAST_UPDAT", "Source"],  # Include "Source"
                        aliases=["Common Name", "Scientific Name", "Date Last Updated", "Source"],  # Matching aliases
                        localize=True,
                        sticky=False,
                        labels=True
                    ),
                    highlight_function=lambda x: {
                        "weight": 2,
                        "color": "#333333",
                        "fillOpacity": 0.8
                    }
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

        st.subheader("Most Common Invasive Species in LA County")
        st.write("Understanding the fire hazards associated with various plant species, especially when dry, is crucial for effective land management and wildfire prevention.")

        species_info = [
            ("Spanish Broom (*Spartium junceum*)", "Highly flammable when dry, contributing significantly to wildfire risks. Its dense growth creates continuous fuel beds, facilitating rapid fire spread. Spanish broom also aggressively displaces native vegetation, reducing biodiversity. It thrives in disturbed areas, forming impenetrable thickets that hinder wildlife movement.", "https://upload.wikimedia.org/wikipedia/commons/9/97/Spartium_junceum_%28habitus%29.jpg"),
            ("Saltcedar (*Tamarix ramosissima*)", "Accumulates salt in its foliage, which can inhibit native plant growth. Its fine, dry leaves and branches are highly combustible, increasing fire intensity in invaded areas. Saltcedar consumes large amounts of water, lowering water tables and altering riparian ecosystems. It also spreads prolifically, outcompeting native species critical for wildlife habitats.", "https://www.invasivespeciesinfo.gov/sites/default/files/styles/extra_large/public/media/image/saltcedar-1624020.jpg?itok=V8IocgSj"),
            ("Giant Reed (*Arundo donax*)", "Highly flammable throughout the year. During dry months, it increases the probability, intensity, and spread of wildfires in riparian environments. Giant reed grows rapidly, forming thick stands that block waterways and exacerbate flooding. Its deep roots make eradication difficult, requiring repeated treatment to prevent regrowth.", "https://upload.wikimedia.org/wikipedia/commons/7/78/Arundo_donax_001.JPG"),
            ("Tree Tobacco (*Nicotiana glauca*)", "A shrubby species that can contribute to fuel loads, especially when dry, potentially aiding fire spread. It produces toxic alkaloids, making it unpalatable for many herbivores, reducing natural control. Its rapid colonization of disturbed areas suppresses native plant regeneration.", "https://upload.wikimedia.org/wikipedia/commons/9/94/Nicotiana_glauca_%288694803666%29.jpg"),
            ("Maltese Star-Thistle (*Centaurea melitensis*)", "Forms dense stands that, when dry, provide fine fuels that ignite easily, increasing fire frequency and intensity. Its spiny, tough stems deter grazing animals, leading to unchecked proliferation. The plant’s deep roots deplete soil moisture, making it harder for native plants to establish.", "https://cdn2.picryl.com/photo/2014/05/02/centaurea-melitensis-flickr-aspidoscelis-50b10a-1024.jpg"),
            ("Cheatgrass (*Bromus tectorum*)", "Dries out early in the summer, leaving vast areas of highly flammable fuel. Increases wildfire frequency and intensity. Cheatgrass spreads aggressively, altering ecosystems by replacing native grasses and reducing forage quality. It also depletes soil nutrients, making it difficult for other plants to grow.", "https://upload.wikimedia.org/wikipedia/commons/b/b8/Cheatgrass%2C_Bromus_tectorum_%2815678709413%29.jpg"),
            ("Cogongrass (*Imperata cylindrica*)", "Highly flammable and creates dense vegetation layers that fuel wildfires, increasing fire intensity. It releases allelopathic chemicals that inhibit native plant growth, leading to monocultures. Its razor-sharp leaves pose a threat to grazing animals and hinder land management efforts.", "https://www.invasivespeciesinfo.gov/sites/default/files/styles/extra_large/public/media/image/cogongrass-5533096.jpg?itok=g7kn4kyw"),
            ("Himalayan Blackberry (*Rubus armeniacus*)", "Highly flammable due to litter and dead canes, acting as a ladder fuel that spreads fires into tree canopies. Its thorny, dense thickets choke out native plants and create barriers for wildlife. Once established, it spreads aggressively through both seeds and root fragments, making eradication difficult.", "https://www.fs.usda.gov/database/feis/plants/shrub/rubspp/flower.jpg"),
            ("Lantana (*Lantana camara*)", "Can change fire patterns by altering the fuel load and increasing the risk of fires spreading to the canopy. Its toxic leaves deter herbivores, reducing natural population control. Lantana aggressively invades pastures, forests, and riparian zones, suppressing native vegetation and biodiversity.", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTDvOA3aAcmKcyWqTEDGq2Qo9bjT2_S68Tg4w&s")
        ]

        for name, description, img_url in species_info:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(img_url, width=150)
            with col2:
                st.markdown(f"### {name}")
                st.write(description)


def main():
    st.set_page_config(layout="wide")
    analysis = InvasivesMap()
    analysis.display()

if __name__ == "__main__":
    main()
