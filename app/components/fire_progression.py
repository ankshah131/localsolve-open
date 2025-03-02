import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import io

# Caching the data fetch function for efficiency
@st.cache_data
def fetch_fire_data():
    CSV_URL = "https://storage.googleapis.com/localsolve_assets/la_wildfires_jan_2025/filtered_la_january_2025_fire_hotspots_combined.csv"
    response = requests.get(CSV_URL)

    if response.status_code == 200:
        csv_data = response.content
        df = pd.read_csv(io.StringIO(csv_data.decode("utf-8")))
        if not df.empty:
            df['acq_date'] = pd.to_datetime(df['acq_date'])
            df['acq_datetime'] = df['acq_date'] + pd.to_timedelta(
                df['acq_time'].astype(str).str.zfill(4).str[:2] + ':' + 
                df['acq_time'].astype(str).str.zfill(4).str[2:] + ':00'
            )
            return df
    return pd.DataFrame()

class FireDataLoader:
    def __init__(self):
        self.df = fetch_fire_data()  # Load cached data
        self.infrastructure = None

# # Fire Progression Class
# class FireProgression:
#     def __init__(self, data_loader):
#         self.data_loader = data_loader
        
# Fire Progression Class
class FireProgression:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        
        if 'map_center' not in st.session_state:
            # Adjusted initial zoom for better default view
            st.session_state.map_center = {'lat': 34.18612130853171, 'lon': -118.337172042249, 'zoom': 10}

    def create_map(self, df_filtered):
        # Use a reliable map style that doesn't require tokens
        fig = px.scatter_mapbox(
            df_filtered,
            lat="latitude",
            lon="longitude",
            color="brightness",
            hover_data={
                "acq_datetime": "|%Y-%m-%d %H:%M",
                "confidence": ":.0f",
                "latitude": ":.2f",
                "longitude": ":.2f",
                "brightness": ":.1f"
            },
            size_max=8,
            opacity=0.7,
            mapbox_style="open-street-map",  # Changed to reliable style
            zoom=st.session_state.map_center['zoom'],
            center={"lat": st.session_state.map_center['lat'], "lon": st.session_state.map_center['lon']},
            color_continuous_scale=px.colors.sequential.YlOrRd,
            labels={'brightness': 'Brightness Temperature (K)'}
        )

        fig.update_traces(
            marker=dict(size=6),
            selector=dict(mode='markers'))

        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            mapbox=dict(bearing=0, pitch=0),
            coloraxis_colorbar=dict(
                title="Brightness Temperature (K)",
                thickness=20,
                len=0.5,
                yanchor="middle",
                y=0.5
            ),
            width=1000,  # Set fixed width for the figure
            height=600   # Ensure height is set in layout as well
        )

        # Update session state with current map view
        if fig.layout.mapbox.center:
            st.session_state.map_center.update({
                'lat': fig.layout.mapbox.center['lat'],
                'lon': fig.layout.mapbox.center['lon'],
                'zoom': fig.layout.mapbox.zoom
            })
            
        return fig
        

    def display(self):
        st.title("Los Angeles Wildfire Progression - January 2025")
    
        df = self.data_loader.df
    
        if not df.empty:
            col1, col2 = st.columns([3, 1.2], gap="large")

            with col1:
                st.subheader("Fire Progression Visualization")
                date_min = df['acq_date'].min().date()
                date_max = df['acq_date'].max().date()

                selected_date = st.slider(
                    "Analysis Date",
                    min_value=date_min,
                    max_value=date_max,
                    value=date_min,
                    format="MM/DD/YYYY"
                )

                df_filtered = df[df['acq_date'].dt.date <= selected_date]

                fig = self.create_map(df_filtered)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("How Fire Progression is Tracked")
                st.markdown("""
                This interactive visualization shows how fires **cumulatively expand over time**:
                
                - Use the **date slider** above to view fire hotspots on specific dates.
                - The **map colors** indicate **thermal intensity**—red/orange for hotter fires, yellow for cooler hotspots.
                - **Larger clusters** of fire hotspots suggest **rapid fire spread**.

                This tool provides valuable insight into wildfire behavior, helping researchers and responders *understand how these fires spread across time**.

                #### Rapid Fire Spread Due to Santa Ana Winds (Jan 7-10)
                The **Santa Ana winds**—strong, dry winds that sweep across Southern California—**significantly accelerated fire spread from January 7-10**. These winds, reaching speeds of **55-70+ mph**, along with dried out vegetation carried embers long distances, fueling the rapid expansion of fires. 
        
                """)

        else:
            st.warning("No data available to display.")

        # Fire Data Explanation BELOW THE MAP AND LEGEND
        st.subheader("Understanding VIIRS Fire Hotspots & Brightness Temperature")
        st.markdown("""
        The **Visible Infrared Imaging Radiometer Suite (VIIRS)** on the Suomi NPP satellite detects fire hotspots using 
        thermal infrared sensing. The data is **sub-daily** with a **spatial resolution of 375 meters**. The key indicators include:

        - **Fire Hotspots:** Each detected point represents an area where active burning is occurring.
        - **Brightness Temperature (K):** Measures the infrared energy emitted by the fire. Higher values indicate more 
          intense heat and combustion.
        - **Confidence Levels:** Indicates the likelihood that the detected heat source is a fire.

        This dataset is valuable for tracking wildfire spread, identifying high-intensity burn areas, and supporting disaster response.
        """)


# Run Streamlit App
if __name__ == "__main__":
    data_loader = FireDataLoader()
    app = FireProgression(data_loader)
    app.display()
if __name__ == "__main__":
    main()
