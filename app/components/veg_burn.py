import streamlit as st
import folium
import requests
import geopandas as gpd
from io import BytesIO
from branca.colormap import LinearColormap
from streamlit_folium import folium_static

import plotly.graph_objects as go
import plotly.express as px

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
    def __init__(self,  data_loader):
        self.data_loader = data_loader
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

    def create_vegetation_burn_severity_chart(self):
        # Get top 10 vegetation types by burn area
        veg_data = self.data_loader.veg_processed
        top10 = veg_data.sort_values(by='Total_Burnt_Area', ascending=False)[:10]
        burn_data = top10[['Class_Cnam', 'Area_of_Burn1', 'Area_of_Burn2', 
                          'Area_of_Burn3', 'Area_of_Burn4']]
        
        return go.Figure(data=[
            go.Bar(name='Low', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn4'], marker_color='#FFFF00'),
            go.Bar(name='Moderate-Low', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn3'], marker_color='#FFA500'),
            go.Bar(name='Moderate-High', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn2'], marker_color='#8B4513'),
            go.Bar(name='High', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn1'], marker_color='#000000')
        ]).update_layout(
            barmode='stack',
            xaxis_tickangle=-45,
            xaxis_title="Species that burned",
            yaxis_title="Area",
            height=700,
            showlegend=True,
            legend=dict(title='Burn Severity', yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

    def create_tree_burn_severity_chart(self):
        trees_data = self.data_loader.trees_withburn
        severity_counts = trees_data.groupby(['sum', 'category'])['species'].count().reset_index()
        severity_counts = severity_counts.sort_values('species', ascending=False)
        print(trees_data[['sum', 'category']])
        
        severity_colors = {
            1: '#7a8737',  # green
            2: '#acbe4d',  # lightgreen
            3: '#0ae042',  # yellow
            4: '#fff70b',  # orange
            5: '#ffaf38',  # red
            6: '#ff641b',  # brown
            7: '#a41fd6'   # black
        }

        
        mode_categories = {
            7: "High Severity",
            6: "Moderate-high Severity",
            5: "Moderate-low Severity",
            4: "Low Severity",
            3: "Unburned",
            2: "Enhanced Regrowth, Low",
            1: "Enhanced Regrowth, High"
        }
        
        fig = go.Figure()
        for severity in sorted(severity_counts['sum'].unique()):
            mask = severity_counts['sum'] == severity
            fig.add_trace(go.Bar(
                x=severity_counts[mask]['category'],
                y=severity_counts[mask]['species'],
                name=mode_categories[severity],  # Using the descriptive category names
                marker_color=severity_colors[severity]
            ))
            
        fig.update_layout(
            barmode='group',
            xaxis_tickangle=-45,
            xaxis_title="Species that burned",
            yaxis_title="Number of trees",
            height=500,
            showlegend=True,
            legend=dict(title='Burn Severity', yanchor="top", y=0.99, xanchor="right", x=0.99)
        )
        return fig

    def create_tree_burn_comparison_chart(self):
        trees_processed = self.data_loader.trees_processed
        return px.scatter(
            trees_processed,
            x='Proportion of trees that burnt',
            y='Proportion of trees that burnt in the 1km buffer',
            size='Total number of trees',
            color='category',
            hover_data=['category', 'Total number of trees'],
            labels={
                'Proportion of trees that burnt': 'Proportion Burnt (Overall)',
                'Proportion of trees that burnt in the 1km buffer': 'Proportion Burnt (1km Buffer)',
                'category': 'Tree Category'
            }
        ).update_layout(
            height=500,
            showlegend=True,
            legend=dict(title='Tree Category', yanchor="top", y=0.99, xanchor="right", x=0.99)
        )
        

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

    def display(self):
        st.title("Vegetation Burn Severity")
        
        # Replace column layout with tabs
        tabs = st.tabs(["Map", "Information", "Charts"])
        
        with tabs[0]:
            with st.spinner("Loading map... This may take a few moments..."):
                m = self.create_map()
                if m is not None:
                    # Make map responsive by removing fixed width
                    #folium_static(m, width=None, height=600)
                    folium_static(m, width=1300, height=600)
        
        with tabs[1]:
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
                "vegetation types.\n\n"

                "Data source - Geospatial data for the Vegetation Mapping Inventory Project of Santa Monica " 
                "Mountains National Recreation Area https://irma.nps.gov/DataStore/Reference/Profile/2272711"

            )
            
            # Add more information about burn severity classes
            st.subheader("Burn Severity Classes")
            for severity, color in BURN_SEVERITY_CLASSES.items():
                st.markdown(f'<div style="background-color:{color}; padding:10px; margin:5px; border-radius:5px;">{severity}</div>', unsafe_allow_html=True)
            
            st.info("The map displays vegetation polygons colored according to their dominant (mode) burn severity category. Click on any polygon to see details.")

        with tabs[2]:
            st.header("Vegetation Burn Analysis for Palisades Fire")
        
            st.subheader("Burn Severity by Vegetation Type")
            st.plotly_chart(
                self.create_vegetation_burn_severity_chart(), 
                use_container_width=True
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Tree Burn Severity by Category")
                st.plotly_chart(
                    self.create_tree_burn_severity_chart(),
                    use_container_width=True
                )
                
            with col2:
                st.subheader("Tree Burn Proportion Comparison")
                st.plotly_chart(
                    self.create_tree_burn_comparison_chart(),
                    use_container_width=True
                )



def main():
    st.set_page_config(layout="wide")
    analysis = VegBurn()
    analysis.display()

if __name__ == "__main__":
    main()
